#!/usr/bin/env python3

from json import load

with open("results.json") as f:
    result = load(f)

for domain, mappings in sorted(result.items()):
    xpaths = set([mapping for mapping, confidence in mappings])
    print(domain, "; ".join(xpaths))

