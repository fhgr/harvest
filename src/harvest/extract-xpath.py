#!/usr/bin/env python3

from lxml import etree

from sys import argv
import re


RE_FILTER_XML_HEADER = re.compile("<\?xml version=\".*? encoding=.*?\?>")


def extract_text(element):
    return ' '.join([t.strip() for t in element.itertext() if t.strip()])


if __name__ == '__main__':
    fname = argv[1]
    xpath = argv[2]

    with open(fname, encoding="utf8") as f:
        html = f.read()
        html = RE_FILTER_XML_HEADER.sub("", html)
        dom = etree.HTML(html)
        for element in dom.xpath(xpath):
            print(element)
            text = extract_text(element)
            print(text)
