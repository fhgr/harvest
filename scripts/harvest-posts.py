#!/usr/bin/env python3

import argparse
import gzip
import logging
import os

from glob import glob
from json import load, dump
from collections import defaultdict
from harvest import posts
from urllib.parse import urlparse

logging.getLogger().setLevel(logging.INFO)

parser = argparse.ArgumentParser(description='Forum harvester - extracts and harvests posts + metadata from Web forums')
parser.add_argument('corpus_path', metavar='corpus_path', help='Path to the input corpus')
parser.add_argument('output_file', metavar='output_file', help='Output file for the parser\'s results.')
parser.add_argument('--debug-directory', dest='debug_directory', help='Optional directory for debug information.')
parser.add_argument('--corpus-include-string', dest='corpus_include_string', help='Optionally restrict the input corpus to URLs that match the corpus include string.')

args = parser.parse_args()


result = defaultdict(list)
for no, fname in enumerate(glob(args.corpus_path + "*.json.gz")):
     opener = gzip.open if fname.endswith(".gz") else open
     with opener(fname) as f:
        forum = load(f)
        domain = urlparse(forum['url']).netloc
        if args.corpus_include_string and not args.corpus_include_string in forum['url']:
            continue

        if args.debug_directory:
            debug_fname = os.path.join(args.debug_directory, "{}-{}.html".format(no, domain))
            with open(debug_fname, "w") as g:
                g.write(forum['html'])

        logging.info("Processing " + forum['url'])
        post = posts.extract_posts(forum)
        result[domain].append(post)

with open(args.output_file, "w") as f:
    dump(result, f, indent=True)

