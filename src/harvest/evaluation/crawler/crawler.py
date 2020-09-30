#!/usr/bin/env python3

import argparse
import logging
import requests
import hashlib
from json import load
from inscriptis import get_text
from fuzzysearch import find_near_matches

from harvest.utils import get_html_dom, get_xpath_tree_text
from harvest.extract import get_forum_date

logging.getLogger().setLevel(logging.INFO)

parser = argparse.ArgumentParser(description='Crawl website to extract web forum')
parser.add_argument('--result-directory', dest='result_directory', help='Directory for storing json results.')

args = parser.parse_args()


def get_normalized_elements(elements, reference_text):
    normalized_elements = []
    start_index = 0
    for element in elements:
        matches = find_near_matches(element, reference_text[start_index:], max_l_dist=30)
        if matches:
            normalized_elements.append(reference_text[start_index:][matches[0].start:matches[0].end])
            start_index += matches[0].end
        else:
            logging.error(f'Failed to find {element}')
            break
    return normalized_elements


with open('config/config.json', 'r') as config_file:
    config = load(config_file)
    for url in config["urls"]:
        response = requests.get(url)
        text = get_text(response.text)
        text = " ".join([c.strip() for c in text.split("\n") if c.strip()])
        corpus_document = {"id": f"i{int(hashlib.md5(url.encode('utf-8')).hexdigest(), 16)}",
                           "url": url,
                           "html": response.text,
                           "text": text}
        dom = get_html_dom(corpus_document["html"])
        forum_posts = get_xpath_tree_text(dom, config["xpath_post_text"])
        forum_dates = get_forum_date(dom, config["xpath_date"], result_as_datetime=False)
        if len(forum_dates) == len(forum_posts):
            normalized_forum_posts = get_normalized_elements(forum_posts, text)
            normalized_forum_posts = get_normalized_elements(forum_posts, text)

