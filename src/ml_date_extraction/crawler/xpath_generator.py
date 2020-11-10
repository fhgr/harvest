#!/usr/bin/env python3

import argparse
import logging
import requests

from harvest import posts

logging.getLogger().setLevel(logging.INFO)

parser = argparse.ArgumentParser(description='Calculate xpath for a forum')
parser.add_argument('url', metavar='url', help='Url to generate xpaths')

args = parser.parse_args()

response = requests.get(args.url)

xpaths = posts.extract_posts({"html": response.text, "url": args.url})
logging.info("----------------------------------------")
logging.info(f"XPath date: {xpaths['date_xpath_pattern']}")
logging.info(f"XPath text: {xpaths['text_xpath_pattern']}")
logging.info(f"XPath user: {xpaths['user_xpath_pattern']}")
logging.info(f"XPath url: {xpaths['url_xpath_pattern']}")
