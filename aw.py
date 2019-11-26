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


from urllib.parse import urlparse
from lxml import etree
from glob import glob
from json import load, dump
from sys import exit

from dragnet import extract_content_and_comments, extract_comments
from inscriptis import get_text

import gzip
import logging
import re
import numpy as np


RE_FILTER_XML_HEADER = re.compile("<\?xml version=\".*? encoding=.*?\?>")
#CORPUS = "../../workspace.python/path-extractor-ai/tests/pathextractor_ai_tests/full_training_data/"
CORPUS = "./data/forum/"

# number of characters required for a match
MATCH_PREFIX_SIZE = 30
VSM_MODEL_SIZE = 5000
VALID_NODE_TYPE_QUALIFIERS = ('class', )

# tags that are not allowed to be part of a forum xpath (lowercase)
BLACKLIST_TAGS = ('/option', '/footer', '/form')

# minimum number of posts we suspect on the page
MIN_POST_COUNT = 3

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
    if not comment.strip():
        return None

    for e in dom.iter():
        text = (e.text or "").strip()
        if text and comment.startswith(text[:MATCH_PREFIX_SIZE]):
            return e

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

def contains_blacklisted_tag(xpath_string, blacklisted_tags):
    '''
    returns
    -------
    True, if the xpath_string contains any blacklisted_tag
    '''
    for tag in blacklisted_tags:
        if tag in xpath_string:
            return True
    return False


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

    divisor = (np.linalg.norm(reference_vsm) * np.linalg.norm(xpath_vsm))
    if not divisor:
        logging.warning("Cannot compute simularity - empty reference (%s) or xpath (%ss) text.", reference_content, ' '.join(xpath_content_list))
        return 0., 1
    similarity = np.dot(reference_vsm, xpath_vsm)/divisor
    return (similarity, xpath_element_count)


result = {}
for no, fname in enumerate(glob(CORPUS + "*.json.gz")):
     opener = gzip.open if fname.endswith(".gz") else open
     with opener(fname) as f:
        print("Opening", fname)
        example = load(f)

        with open("%s.html" % no, "w") as g:
            g.write(example['html'])


        if not 'maladiesrares' in example['url']:
            continue

        print(example['url'])
        domain = urlparse(example['url']).netloc

        if domain not in result:
            result[domain] = []

        html = RE_FILTER_XML_HEADER.sub("", example['html'])
        dom = etree.HTML(html)
        tree = etree.ElementTree(dom)
        content_comments = extract_comments(example['html']).strip()

        comments = []
        # remove blacklisted items and use inscriptis if dragnet has failed
        for comment in [c for c in (content_comments.split("\n") if content_comments else get_text(html).split()) if c.strip()]:
            if not comment.strip():
                continue
            elif not 'copyright' in comment.lower():
                comments.append(comment)
            else:
                break
        reference_content = " ".join(comments)

        candidate_xpaths = []
        for comment in comments:
            xpath = get_xpath_tree(comment, dom, tree)
            if not xpath or contains_blacklisted_tag(xpath, BLACKLIST_TAGS):
                continue
            xpath_pattern = get_xpath(comment, dom)

            xpath_score, xpath_element_count = assess_node(reference_content=reference_content, dom=dom, xpath=xpath_pattern)
            if xpath_element_count > 1:
                candidate_xpaths.append((xpath_score, xpath_element_count, xpath_pattern))

        if not candidate_xpaths:
            print("Couldn't identify any candidate posts for forum", example['url'])
            result[domain].append({'url': example['url'], 'dragnet': content_comments})
            continue


        # obtain anchor node
        candidate_xpaths.sort()
        xpath_score, xpath_element_count, xpath_pattern = candidate_xpaths.pop()

        while True:
            new_xpath_pattern = xpath_pattern + "/.."
            new_xpath_score, new_xpath_element_count = assess_node(reference_content=content_comments, dom=dom, xpath=new_xpath_pattern)
            if new_xpath_element_count < MIN_POST_COUNT:
                break

            xpath_pattern = new_xpath_pattern
            xpath_score = new_xpath_score

        print(no, "Obtained most likely forum xpath for forum", example['url'] + ":", xpath_pattern, "with a node score of", xpath_score)
        if xpath_pattern:
            forum_posts = [extract_text(element) for element in dom.xpath(xpath_pattern)]
        result[domain].append({'url': example['url'], 'xpath_pattern': xpath_pattern, 'xpath_score': xpath_score, 'forum_posts': forum_posts, 'dragnet': content_comments})


with open("results.json", "w") as f:
    dump(result, f, indent=True)

