#!/usr/bin/env python3

import logging
import os

from json import dump
from urllib.parse import urlparse

logging.getLogger().setLevel(logging.INFO)


def write_to_json(url, result_directory, document):
    url = urlparse(url).netloc + urlparse(url).path + urlparse(url).params
    result_fname = os.path.join(result_directory, f'{url.replace("/", ".")}.json')
    if not os.path.exists(result_directory):
        os.makedirs(result_directory)
    if not os.path.isfile(result_fname):
        with open(result_fname, "w") as f2:
            dump(document, f2, indent=True)
