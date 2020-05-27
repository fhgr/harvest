#!/usr/bin/env python3

import argparse
import logging
import re

from glob import glob
from json import load, dump
from collections import defaultdict
from urllib.parse import urlparse

logging.getLogger().setLevel(logging.INFO)


def add_start_end(element_to_add, text, sub_text, start_index):
    start_index = text.find(sub_text, start_index)
    if start_index > -1:
        element_to_add['start'] = start_index
        element_to_add['end'] = start_index + len(sub_text)
    else:
        logging.warning(f'Not found in text:\n{sub_text}')
    return start_index


def remove_unused_links(text, links_to_keep):
    pattern = re.compile(r'( \* )?\[[^\]]*\]\((http(s)?:\/)?\/[^\)]*\)')
    start_index = 0
    while start_index > -1:
        link_match = pattern.search(text, start_index)
        if link_match:
            link_extracted = re.search(r'(http(s)?:\/)?\/[^\)]*', link_match.group(0))
            if link_extracted and link_extracted.group(0) not in links_to_keep:
                logging.info(f'Removed {link_match.group(0)}')
                only_text = re.search(r'\[.*\]', link_match.group(0))
                text = text[:link_match.start()] + only_text.group(0)[1:-1] + text[link_match.end():]
            else:
                start_index = link_match.end()
        else:
            start_index = -1
    return text


parser = argparse.ArgumentParser(description='Forum harvester - remove unused link from text')
parser.add_argument('pre_gold_document_path', metavar='pre_gold_document_path',
                    help='Path to the pre processed gold documents')
parser.add_argument('--corpus-include-string', dest='corpus_include_string',
                    help='Optionally restrict the input corpus to URLs that match the corpus include string.')

args = parser.parse_args()

result = defaultdict(list)
for no, fname in enumerate(glob(args.pre_gold_document_path + "*.json")):
    with open(fname, "r") as f:
        forum = load(f)
        if args.corpus_include_string and args.corpus_include_string not in forum['url']:
            continue

        logging.info("Remove unused links for " + forum['url'])
        link_user = set(x['user']['surface_form'] for x in forum['gold_standard_annotation'] if
                        'user' in x and urlparse(x['user']['surface_form']).netloc)
        link_post = set(x['post_link']['surface_form'] for x in forum['gold_standard_annotation'] if
                        'post_link' in x and urlparse(x['post_link']['surface_form']).netloc)

        forum['text'] = remove_unused_links(forum['text'], link_user.union(link_post))
        with open(fname, "w") as f2:
            dump(forum, f2, indent=True)
