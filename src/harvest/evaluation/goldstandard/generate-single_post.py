#!/usr/bin/env python3

import argparse
import logging
import os
from collections import defaultdict
from glob import glob
from json import load

from harvest.evaluation.goldstandard.file import write_to_json, get_file_path

logging.getLogger().setLevel(logging.INFO)

parser = argparse.ArgumentParser(description='Forum harvester - generate gold standard documents with only one post')
parser.add_argument('gold_document_path', metavar='gold_document_path', help='Path to the gold documents')
parser.add_argument('--result-directory', dest='result_directory', help='Optional directory for storing final results.')
parser.add_argument('--corpus-include-string', dest='corpus_include_string',
                    help='Optionally restrict the input corpus to URLs that match the corpus include string.')

args = parser.parse_args()

result = defaultdict(list)
for no, fname in enumerate(glob(args.gold_document_path + "*.json")):
    with open(fname) as f:
        forum = load(f)
        if (args.corpus_include_string and args.corpus_include_string not in forum['url']) \
                or os.path.isfile(get_file_path(forum['url'], args.result_directory)):
            continue

        logging.info("Start creating final gold standard document with only one post for " + forum['url'])

        single_post = " ".join([a['post_text']['surface_form'] for a in forum['gold_standard_annotation']])
        start_index = forum['gold_standard_annotation'][0]['post_text']['start']
        end_index = forum['gold_standard_annotation'][-1]['post_text']['end']

        forum['gold_standard_annotation'] = [{
            "post_text": {
                "surface_form": single_post,
                "start": start_index,
                "end": end_index
            }
        }]

        write_to_json(os.path.basename(fname), args.result_directory, forum)
