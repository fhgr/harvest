#!/usr/bin/env python3

from json import load

with open("results.json") as f:
    result = load(f)

for domain, values in sorted(result.items()):
    for value in values:
        print("%s: Posts: %s; URL: %s --> Source: %s" % (domain, value["xpath_pattern"], value.get("url_xpath_pattern", "-"), value["url"]))

