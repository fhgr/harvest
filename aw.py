#!/usr/bin/env python3

from dragnet import extract_content_and_comments, extract_comments
from lxml import etree
from glob import glob
from json import load

from sys import exit

import re
import numpy as np


RE_FILTER_XML_HEADER = re.compile("<\?xml version=\".*? encoding=.*?\?>")
CORPUS = "../../workspace.python/path-extractor-ai/tests/pathextractor_ai_tests/full_training_data/"

# number of characters required for a match
MATCH_PREFIX_SIZE = 30
VSM_MODEL_SIZE = 5000
VALID_NODE_TYPE_QUALIFIERS = ('class', )

# background knowledge to include:
# - blacklist hmlt/head, aside, ...

# simplifications:
# - only consider tags with a class attribute
# - vsm based on the hashing trick

def text_to_vsm(text):
    '''
    translates a text into the vector space model
    using the hashing trick.

    VSM_MODEL_SIZE determines the size of the vsm.
    '''
    vms = np.full(VSM_MODEL_SIZE, 0)
    for word in text.split():
        index = word.__hash__() % VSM_MODEL_SIZE
        word[index] += 1
    return vms


def get_xpath_tree_text(dom, xpath):
    return extract_text(dom.xpath(xpath))


def extract_text(element):
    ''' obtains the text for the given element '''
    return ' '.join([t.strip() for t in element.itertext() if t.strip()])


def get_matching_element(comment, dom):
    '''
    returns
    -------
    the element that matches the given comment
    '''
    for e in dom.iter():
        text = (e.text or "").strip()
        if text and comment.startswith(text[:MATCH_PREFIX_SIZE]):
            return e

    print("Cannot find path for comment >>>" + comment + "<<<")
    return None


def get_xpath_expression(element):
    '''
    returns
    -------
    the xpath expression for the given element
    '''
    attr_filter = " & ".join(['%s="%s"' % (key, value) for key, value in element.attrib.items() if key in VALID_NODE_TYPE_QUALIFIERS])
    if attr_filter:
        return element.tag + "[%s]" % attr_filter
    else:
        return element.tag
    
 
def get_xpath(comment, dom):
    '''
    returns
    -------
    the xpath for the given comment.
    '''
    xpath_list = []
    has_class_filter = False
    element = get_matching_element(comment, dom)

    while not has_class_filter and element:
        xpath_expression = get_xpath_expression(element)
        has_class_filter = "[" in xpath_expression
        xpath_list.append(xpath_expression)

        element = element.getparent()

    xpath_list.reverse()
    return "/".join(xpath_list)


def get_xpath_tree(comment, dom, tree):
    element = get_matching_element(comment, dom)
    return None if element is None else tree.getpath(element)


def get_similarity_metric(reference_content, dom, xpath):
    '''
    returns
    -------
    a metric based on the vector space model that indicates
    how well the given xpath fits the reference content.
    '''
    reference = text_to_vsm(reference_content)
    xpath_content = text_to_vsm(get_xpath_tree_text(dom, xpath))
    return np.dot(reference, xpath_content)/(np.linalg.norm(reference) * np.linalg.norm(xpath_content))


for no, fname in enumerate(glob(CORPUS + "/*.json")):
    with open(fname) as f:
        example = load(f)

        with open("%s.html" % no, "w") as g:
            g.write(example['html'])

        print(example['url'])

        html = RE_FILTER_XML_HEADER.sub("", example['html'])
        dom = etree.HTML(html)
        tree = etree.ElementTree(dom)
        content_comments = extract_comments(example['html'])
        for comment in content_comments.split("\n"):
            xpath = get_xpath_tree(comment, dom, tree)
            print(xpath, '-->', get_xpath(comment, dom))
        exit(0)
