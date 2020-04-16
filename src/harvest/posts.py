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

# todo
# ====
# * post metadata extraction framework
# * post cleanup framework

# simplifications:
# ================
# - only consider tags with a class attribute
# - vsm based on the hashing trick

# algorithm
# =========
# - match text to xpath nodes
# - extract the text based on the xpath nodes and determine the best match
#   based on the node + its children
# - from the best match that yields multiple results (i.e. forum posts)
#   select node parent elements as long as we still get the same number of
#   results.
# - constraints
#   - blocked tags are not allowed to appear down- or upstream of the selected
#     path (e.g. it is not possible that a forum post contains a 'form' or
#     'input' element :)
#   - there are forums that are contained in a form tag ....
#   - changed algorithm:
#     - do not let additional BLACKLIST_TAGS be entered
#     - strongly discount paths that contain BLACKLIST_TAGS

# open issues
# -----------
# * mumsnet -> does not detect first post (//div[@class="talk-post  message"]/p/../.."]) rather than //div[@class="post "])
# * amsel.de -> only get's every second post (//td[@class="forum_message bg_7"]/..) due to different coloring ...
# * www.msconnection.org, shift.ms -> works well, but does not get the title of the first post

# determine post URL
# ------------------
# * relevant tags: <a> (href or name)
# * point to the same domain, or even better also to the same page (without parameters)
# * appear always in the same element

# cleanup posts
# -------------
# * remove repeated elements
# * appear at the beginning or end of a post
# * may contain information on
#   - user
#   - date (subscription versus post date) => always compare dates within a page for computing the date extraction rule
#   - replies, likes, etc.

# suggestions
# -----------
# * remove posts that exceed a certain length and URL threshold (spam) - compare: http://blog.angelman-asa.org (liuchunkai)

from itertools import chain

from harvest.cleanup.forum_post import remove_boilerplate
from harvest.utils import (get_xpath_expression, extract_text, get_html_dom,
                           get_xpath_tree_text, replace_xpath_last_class_with_and_condition)
from harvest.metadata.link import get_link
from harvest.metadata.date import get_date
from harvest.metadata.username import get_user
from dragnet import extract_content_and_comments, extract_comments
from inscriptis import get_text

from lxml import etree
import logging
import numpy as np

# CORPUS = "../../workspace.python/path-extractor-ai/tests/pathextractor_ai_tests/full_training_data/"
CORPUS = "./data/forum/"

# number of characters required for a match
MATCH_PREFIX_SIZE = 30
VSM_MODEL_SIZE = 5000

# tags that are not allowed to be part of a forum xpath (lowercase)
BLACKLIST_TAGS = ('option', 'footer', 'form', 'aside', 'head', 'tfoot')

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


def get_xpath_tree(comment, dom, tree):
    element = get_matching_element(comment, dom)
    return (None, None) if element is None else (element, tree.getpath(element))


def decendants_contain_blacklisted_tag(xpath, dom, blacklisted_tags):
    decendants = set([t.tag for t in chain(*[e.iterdescendants() for e in dom.xpath(xpath)])])
    for tag in blacklisted_tags:
        if tag in decendants:
            return True
    return False


def ancestors_contains_blacklisted_tag(xpath_string, blacklisted_tags):
    '''
    returns
    -------
    True, if the xpath_string (i.e. the ancestors) contains any blacklisted_tag
    '''
    xpath = xpath_string.split("/")
    for tag in blacklisted_tags:
        if tag in xpath:
            return True
    return False


def assess_node(reference_content, dom, xpath, blacklisted_tags):
    '''
    returns
    -------
    a metric that is based on
      (i) the vector space model and
     (ii) the number of returned elements
    (iii) whether the descendants contain any blacklisted tags
    to assess whether the node is likely to be part of a forum post.
    '''
    if xpath == "//" or decendants_contain_blacklisted_tag(xpath, dom, blacklisted_tags):
        return 0., 1

    xpath_content_list = get_xpath_tree_text(dom, xpath)
    xpath_element_count = len(xpath_content_list)

    reference_vsm = text_to_vsm(reference_content)
    xpath_vsm = text_to_vsm(' '.join(xpath_content_list))

    divisor = (np.linalg.norm(reference_vsm) * np.linalg.norm(xpath_vsm))
    if not divisor:
        logging.warning("Cannot compute similarity - empty reference (%s) or xpath (%ss) text.", reference_content,
                        ' '.join(xpath_content_list))
        return 0., 1
    similarity = np.dot(reference_vsm, xpath_vsm) / divisor

    # discount any node that contains BLACKLIST_TAGS
    if ancestors_contains_blacklisted_tag(xpath, BLACKLIST_TAGS):
        similarity /= 10
    return (similarity, xpath_element_count)


def extract_posts(forum):
    dom = get_html_dom(forum['html'])
    tree = etree.ElementTree(dom)
    # content_comments = extract_comments(forum['html']).strip()

    comments = []
    # remove blacklisted items and use inscriptis if dragnet has failed
    content_comments = get_text(forum['html'])
    for comment in [c for c in content_comments.split("\n") if c.strip()]:
        if not comment.strip():
            continue
        elif 'copyright' not in comment.lower():
            comments.append(comment.strip())
        else:
            break
    reference_content = " ".join(comments)

    candidate_xpaths = []
    logging.debug("Extracted %d lines of comments.", len(comments))
    for comment in comments:
        element, xpath = get_xpath_tree(comment, dom, tree)
        logging.debug("Processing commment '%s' with xpath '%s'.", comment, xpath)
        if not xpath:
            continue
        element = get_matching_element(comment, dom)
        xpath_pattern = get_xpath_expression(element)

        xpath_score, xpath_element_count = assess_node(reference_content=reference_content, dom=dom,
                                                       xpath=xpath_pattern, blacklisted_tags=BLACKLIST_TAGS)
        if xpath_element_count > 1:
            candidate_xpaths.append((xpath_score, xpath_element_count, xpath_pattern))

    if not candidate_xpaths:
        logging.warning("Couldn't identify any candidate posts for forum", forum['url'])
        return {'url': forum['url'], 'dragnet': content_comments}

    # obtain anchor node
    candidate_xpaths.sort()
    xpath_score, xpath_element_count, xpath_pattern = candidate_xpaths.pop()

    while True:
        new_xpath_pattern = xpath_pattern + "/.."
        new_xpath_score, new_xpath_element_count = assess_node(reference_content=content_comments, dom=dom,
                                                               xpath=new_xpath_pattern, blacklisted_tags=BLACKLIST_TAGS)
        if new_xpath_element_count < MIN_POST_COUNT:  #
            break

        xpath_pattern = new_xpath_pattern
        xpath_score = new_xpath_score

    logging.info("Obtained most likely forum xpath for forum %s: %s with a score of %s.", forum['url'], xpath_pattern,
                 xpath_score)
    if xpath_pattern:
        xpath_pattern = replace_xpath_last_class_with_and_condition(xpath_pattern)
        forum_posts = get_xpath_tree_text(dom, xpath_pattern)
        forum_posts = remove_boilerplate(forum_posts)

    result = {'url': forum['url'], 'xpath_pattern': xpath_pattern,
              'xpath_score': xpath_score, 'forum_posts': forum_posts,
              'dragnet': None, 'url_xpath_pattern': None,
              'date_xpath_pattern': None, 'user_xpath_pattern': None}

    # add the post URL
    url_xpath_pattern = get_link(dom, xpath_pattern, forum['url'], forum_posts)
    if url_xpath_pattern:
        result['url_xpath_pattern'] = url_xpath_pattern

    # add the post Date
    date_xpath_pattern = get_date(dom, xpath_pattern, forum['url'],
                                  forum_posts)
    if date_xpath_pattern:
        result['date_xpath_pattern'] = date_xpath_pattern

    # add the post user
    user_xpath_pattern = get_user(dom, xpath_pattern, forum['url'], forum_posts)
    if user_xpath_pattern:
        result['user_xpath_pattern'] = user_xpath_pattern
    print(">>>", user_xpath_pattern)
    return result
