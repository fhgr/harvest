#!/usr/bin/env python3

import argparse
import logging
import requests
import hashlib
import os
from urllib.parse import urlparse
from json import load, dump

from harvest.utils import get_html_dom, get_xpath_tree_text
from harvest.extract import get_forum_date

logging.getLogger().setLevel(logging.INFO)

parser = argparse.ArgumentParser(description='Crawl website to extract date from web forum')
parser.add_argument('--result-directory', dest='result_directory', help='Directory for storing json results.')

args = parser.parse_args()


def save_json(url, corpus_document):
    file_name = f'{urlparse(url).path.split("/")[-1] + urlparse(url).params + urlparse(url).query}.json'
    folder_structure = os.path.join(args.result_directory, urlparse(url).hostname)
    file_name = os.path.join(folder_structure, file_name)
    if not os.path.exists(folder_structure):
        os.makedirs(folder_structure)
    if not os.path.isfile(file_name):
        with open(file_name, "w") as f:
            dump(corpus_document, f, indent=True)


def start_crawl():
    with open('config/config.json', 'r') as config_file:
        config = load(config_file)
        for url in config["urls"]:
            response = requests.get(url)
            corpus_document = {"id": f"i{int(hashlib.md5(url.encode('utf-8')).hexdigest(), 16)}",
                               "url": url, "xpath_date": config["xpath_date"],
                               "html": response.text,
                               "gold_standard_annotation": []}
            dom = get_html_dom(corpus_document["html"])
            forum_posts = get_xpath_tree_text(dom, config["xpath_post_text"])
            forum_dates = get_forum_date(dom, config["xpath_date"], result_as_datetime=False)
            if len(forum_dates) == len(forum_posts):
                for post_number, forum_date in enumerate(forum_dates):
                    corpus_document["gold_standard_annotation"].append({"datetime": {
                        "surface_form": forum_date,
                        "post_number": post_number
                    }})
                save_json(url, corpus_document)
            else:
                logging.warning(f'{url} date could not be extracted')


start_crawl()
