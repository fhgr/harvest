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

# with open('config/config.json', 'r') as config_file:
#     config = load(config_file)
#     for url in config["urls"]:
#         response = requests.get(url)
#         corpus_document = {"id": f"i{int(hashlib.md5(url.encode('utf-8')).hexdigest(), 16)}",
#                            "url": url,
#                            "html": response.text,
#                            "text": get_text(response.text)}
#         dom = get_html_dom(corpus_document["html"])
#         forum_posts = get_xpath_tree_text(dom, config["xpath_post_text"])
#         forum_dates = get_forum_date(dom, config["xpath_date"], result_as_datetime=False)
#         test = 1
