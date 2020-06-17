#!/usr/bin/env python3

import argparse
import logging
import os

from glob import glob
from json import load
from collections import defaultdict
from harvest.evaluation.goldstandard.file import write_to_json, get_file_path

logging.getLogger().setLevel(logging.INFO)


def add_start_end(element_to_add, text, sub_text, start_index):
    start_index = text.find(sub_text, start_index)
    if start_index > -1:
        element_to_add['start'] = start_index
        element_to_add['end'] = start_index + len(sub_text)
        return start_index + len(sub_text)
    else:
        logging.warning(f'Not found in text:\n{sub_text}')
        return -1


parser = argparse.ArgumentParser(description='Forum harvester - generate final gold standard documents')
parser.add_argument('pre_gold_document_path', metavar='pre_gold_document_path',
                    help='Path to the pre processed gold documents')
parser.add_argument('--result-directory', dest='result_directory', help='Optional directory for storing final results.')
parser.add_argument('--corpus-include-string', dest='corpus_include_string',
                    help='Optionally restrict the input corpus to URLs that match the corpus include string.')

args = parser.parse_args()

result = defaultdict(list)
for no, fname in enumerate(glob(args.pre_gold_document_path + "*.json")):
    with open(fname) as f:
        forum = load(f)
        if (args.corpus_include_string and args.corpus_include_string not in forum['url']) \
                or os.path.isfile(get_file_path(forum['url'], args.result_directory)):
            continue

        logging.info("Start creating final gold standard document for " + forum['url'])
        search_start_index = 0
        all_indexes_found = True
        for post in forum['gold_standard_annotation']:
            index_post_text = [add_start_end(post['post_text'], forum['text'], post['post_text']['surface_form'],
                                             search_start_index),
                               add_start_end(post['datetime'], forum['text'], post['datetime']['surface_form'],
                                             search_start_index),
                               add_start_end(post['user'], forum['text'], post['user']['surface_form'],
                                             search_start_index)]
            if 'post_link' in post:
                index_post_text.append(add_start_end(post['post_link'], forum['text'],
                                                     post['post_link']['surface_form'], search_start_index))
            max_index = max(index_post_text)
            if max_index > -1:
                search_start_index = max_index
            if min(index_post_text) < 0:
                all_indexes_found = False
        if all_indexes_found:
            write_to_json(forum['url'], args.result_directory, forum)
            logging.info('Gold standard document successfully created')
        else:
            logging.warning('Not all indexes found. Check pre file again.')
