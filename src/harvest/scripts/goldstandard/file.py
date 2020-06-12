#!/usr/bin/env python3

import logging
import os

from json import dump
from urllib.parse import urlparse

logging.getLogger().setLevel(logging.INFO)


def get_file_path(url, result_directory):
    url = urlparse(url).netloc + urlparse(url).path + urlparse(url).params
    return os.path.join(result_directory, f'{url.replace("/", ".")}.json')


def write_to_json(url, result_directory, document):
    result_fname = get_file_path(url, result_directory)
    if not os.path.exists(result_directory):
        os.makedirs(result_directory)
    if not os.path.isfile(result_fname):
        with open(result_fname, "w") as f2:
            dump(document, f2, indent=True)
