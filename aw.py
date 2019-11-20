#!/usr/bin/env python3

# Forum Extraction AI and heuristic
# ---------------------------------
# (C)opyrights 2019 Albert Weichselbraun

# potential improvements
# ======================
#
# - include background knowledge
#   - blacklist hmlt/head, aside, ...
# - remove text found in blacklisted paths, to increase the metric's accuracy

# simplifications:
# ================
# - only consider tags with a class attribute
# - vsm based on the hashing trick

# algorithm
# =========
# - match text to xpath nodes
# - extract the text based on the xpath nodes and determine the best match based on the node + its children
# - from the best match that yields multiple results (i.e. forum posts) select node parent elements as long as we still get the same number of results


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

def text_to_vsm(text):
    '''
    translates a text into the vector space model
    using the hashing trick.

    VSM_MODEL_SIZE determines the size of the vsm.
    '''
    vms = np.full(VSM_MODEL_SIZE, 0)
    for word in text.split():
        index = word.__hash__() % VSM_MODEL_SIZE
        vms[index] += 1
    return vms


def get_xpath_tree_text(dom, xpath):
    '''
    returns
    -------
    a list of text obtained by all elements matching the given xpath
    '''
    return [extract_text(element) for element in dom.xpath(xpath)]

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
    attr_filter = " & ".join(['@%s="%s"' % (key, value) for key, value in element.attrib.items() if key in VALID_NODE_TYPE_QUALIFIERS])
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

    while not has_class_filter and element is not None:
        xpath_expression = get_xpath_expression(element)
        has_class_filter = "[" in xpath_expression
        xpath_list.append(xpath_expression)

        element = element.getparent()

    xpath_list.reverse()
    return "//" + "/".join(xpath_list)


def get_xpath_tree(comment, dom, tree):
    element = get_matching_element(comment, dom)
    return None if element is None else tree.getpath(element)


def assess_node(reference_content, dom, xpath):
    '''
    returns
    -------
    a metric that is based on 
      (i) the vector space model and
     (ii) the number of returned elements
    to assess whether the node is likely to be part of a forum post.
    '''
    if xpath == "//":
        return 0., 1

    xpath_content_list = get_xpath_tree_text(dom, xpath)
    xpath_element_count = len(xpath_content_list)

    reference_vsm = text_to_vsm(reference_content)
    xpath_vsm = text_to_vsm(' '.join(xpath_content_list))

    similarity = np.dot(reference_vsm, xpath_vsm)/(np.linalg.norm(reference_vsm) * np.linalg.norm(xpath_vsm))
    return (similarity, xpath_element_count)


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

        candidate_xpaths = []
        for comment in content_comments.split("\n"):
            xpath = get_xpath_tree(comment, dom, tree)
            xpath_pattern = get_xpath(comment, dom)

            xpath_score, xpath_element_count = assess_node(reference_content=content_comments, dom=dom, xpath=xpath_pattern)
            if xpath_element_count > 1:
                candidate_xpaths.append((xpath_score, xpath_element_count, xpath_pattern))

        # obtain anchor node
        candidate_xpaths.sort()
        xpath_score, xpath_element_count, xpath_pattern = candidate_xpaths.pop()

        while True:
            new_xpath_pattern = xpath_pattern + "/.."
            new_xpath_score, new_xpath_element_count = assess_node(reference_content=content_comments, dom=dom, xpath=new_xpath_pattern)
            if new_xpath_element_count < min(3, xpath_element_count/2):
                break

            xpath_pattern = new_xpath_pattern
            xpath_score = new_xpath_score

        print("Obtained most likely forum xpath:", xpath_pattern, "with a node score of", xpath_score)

        exit(0)


