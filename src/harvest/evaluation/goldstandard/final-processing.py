#!/usr/bin/env python3

import argparse
import logging
import os

from glob import glob
from json import load
from collections import defaultdict
from harvest.evaluation.goldstandard.file import write_to_json, get_file_path
from harvest.evaluation.goldstandard.calculate_position import get_start_end_for_post

logging.getLogger().setLevel(logging.INFO)

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
            max_index = get_start_end_for_post(post, forum['text'], search_start_index)
            if max_index > -1:
                search_start_index = max_index
            else:
                all_indexes_found = False
        if all_indexes_found:
            write_to_json(forum['url'], args.result_directory, forum)
            logging.info('Gold standard document successfully created')
        else:
            logging.warning('Not all indexes found. Check pre file again.')
