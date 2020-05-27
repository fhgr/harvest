#!/usr/bin/env python3

import argparse
import gzip
import logging

from glob import glob
from json import load
from inscriptis import get_text
from inscriptis.model.config import ParserConfig
from collections import defaultdict
from harvest import posts
from harvest.extract import extract_posts
from urllib.parse import urlparse

from scripts.goldstandard.file import write_to_json

logging.getLogger().setLevel(logging.INFO)

parser = argparse.ArgumentParser(description='Forum harvester - generate gold standard document for further processing')
parser.add_argument('corpus_path', metavar='corpus_path', help='Path to the input corpus')
parser.add_argument('--result-directory', dest='result_directory', help='Optional directory for storing json results.')
parser.add_argument('--corpus-include-string', dest='corpus_include_string',
                    help='Optionally restrict the input corpus to URLs that match the corpus include string.')

args = parser.parse_args()

result = defaultdict(list)
for no, fname in enumerate(glob(args.corpus_path + "*.json.gz")):
    opener = gzip.open if fname.endswith(".gz") else open
    with opener(fname) as f:
        forum = load(f)
        domain = urlparse(forum['url']).netloc
        if args.corpus_include_string and args.corpus_include_string not in forum['url']:
            continue

        logging.info("Processing " + forum['url'])
        postXPath = posts.extract_posts(forum)
        if postXPath['xpath_pattern']:
            config = ParserConfig(display_links=True, display_anchors=True)
            text = get_text(forum['html'], config)
            text = " ".join([c.strip() for c in text.split("\n") if c.strip()])
            document = {"url": forum['url'], "html": forum['html'], "text": text, "gold_standard_annotation": []}

            if args.result_directory:
                for post in extract_posts(forum['html'], forum['url'],
                                          postXPath['xpath_pattern'],
                                          postXPath['url_xpath_pattern'],
                                          postXPath['date_xpath_pattern'],
                                          postXPath['user_xpath_pattern'], result_as_datetime=False):
                    post_element = {"post_text": {"text": post.post},
                                    "datetime": {"datetime": post.date},
                                    "user": {"user": post.user}}
                    if postXPath['url_xpath_pattern']:
                        post_element["post_link"] = {"link": post.url}
                    document["gold_standard_annotation"].append(post_element)

                write_to_json(forum['url'], args.result_directory, document)
        else:
            logging.error(f'Could not process {forum["url"]}')
