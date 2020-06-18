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

from harvest.cleanup.forum_post import remove_boilerplate
from harvest.utils import (get_xpath_expression, get_html_dom, get_xpath_combinations_for_classes,
                           get_xpath_tree_text)
from harvest.metadata.link import get_link
from harvest.metadata.date import get_date
from harvest.metadata.username import get_user
from harvest.metadata.usertext import get_text_xpath_pattern
from harvest.similarity_calculator import assess_node
from inscriptis import get_text

from lxml import etree
import logging
import re

CORPUS = "./data/forum/"

# number of characters required for a match
MATCH_PREFIX_SIZE = 30

BLACKLIST_POST_TEXT_TAG = ('h1', 'h2', 'h3', 'h4', 'h5', 'a')

# minimum number of posts we suspect on the page
MIN_POST_COUNT = 3


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
        min_length_of_text = len(comment[:MATCH_PREFIX_SIZE])
        if text and comment.startswith(text[:MATCH_PREFIX_SIZE]) and len(text) >= min_length_of_text and \
                e.tag is not etree.Comment:
            return e

    return None


def get_xpath_tree(comment, dom, tree):
    element = get_matching_element(comment, dom)
    return (None, None) if element is None else (element, tree.getpath(element))


def _remove_trailing_p_element(xpath):
    """
    The p elements at the end can be removed. Some posts have several p elements and some have none at all.
    Those without p element can then not be detected. As Example, leading post can not be detected:
    https://us.forums.blizzard.com/en/wow/t/layers-and-character-creation-adjustments-on-select-realms/499760

    Args:
        xpath: the xpath to remove the p element from

    Returns:

    """
    return re.sub(r'(?<!([\/]))\/p$', '', xpath)


def extract_posts(forum):
    dom = get_html_dom(forum['html'])
    tree = etree.ElementTree(dom)

    comments = []
    # remove blacklisted items
    content_comments = get_text(forum['html'])
    for comment in (c for c in content_comments.split("\n") if c.strip()):
        if 'copyright' not in comment.lower():
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
        if element.tag not in BLACKLIST_POST_TEXT_TAG:
            xpath_pattern = get_xpath_expression(element)
            xpath_pattern = _remove_trailing_p_element(xpath_pattern)

            xpath_score, xpath_element_count = assess_node(reference_content=reference_content, dom=dom,
                                                           xpath=xpath_pattern, reward_classes=True)
            if xpath_element_count > 1:
                candidate_xpaths.append((xpath_score, xpath_element_count, xpath_pattern))

    if not candidate_xpaths:
        logging.warning("Couldn't identify any candidate posts for forum", forum['url'])
        return {'url': forum['url'], 'dragnet': None, 'url_xpath_pattern': None, 'xpath_pattern': None,
                'xpath_score': None, 'forum_posts': None,
                'date_xpath_pattern': None, 'user_xpath_pattern': None, 'text_xpath_pattern': None}

    # obtain anchor node
    candidate_xpaths.sort()
    xpath_score, xpath_element_count, xpath_pattern = candidate_xpaths.pop()

    while True:
        new_xpath_pattern = xpath_pattern + "/.."
        new_xpath_score, new_xpath_element_count = assess_node(reference_content=content_comments, dom=dom,
                                                               xpath=new_xpath_pattern)
        if new_xpath_element_count < MIN_POST_COUNT:  #
            break

        xpath_pattern = new_xpath_pattern
        xpath_score = new_xpath_score

    # Check if combinations of classes result in detecting leading post
    candidate_xpaths = []
    for final_xpath in get_xpath_combinations_for_classes(xpath_pattern):
        new_xpath_score, new_xpath_element_count = assess_node(reference_content=reference_content, dom=dom,
                                                               xpath=final_xpath)
        if (xpath_element_count < new_xpath_element_count <= xpath_element_count + 2 or
            xpath_element_count * 2 - new_xpath_element_count in range(-1, 2)) and new_xpath_score > xpath_score:
            candidate_xpaths.append((new_xpath_score, new_xpath_element_count, final_xpath))

    if candidate_xpaths:
        candidate_xpaths.sort()
        xpath_score, xpath_element_count, xpath_pattern = candidate_xpaths.pop()

    logging.info(
        f"Obtained most likely forum xpath for forum {forum['url']}: {xpath_pattern} with a score of {xpath_score}.")
    if xpath_pattern:
        forum_posts = get_xpath_tree_text(dom, xpath_pattern)
        forum_posts = remove_boilerplate(forum_posts)

    result = {'url': forum['url'], 'xpath_pattern': xpath_pattern,
              'xpath_score': xpath_score, 'forum_posts': forum_posts,
              'dragnet': None, 'url_xpath_pattern': None,
              'date_xpath_pattern': None, 'user_xpath_pattern': None, 'text_xpath_pattern': None}

    if xpath_pattern:
        result['text_xpath_pattern'] = get_text_xpath_pattern(dom, xpath_pattern, forum_posts)

    # add the post URL
    url_xpath_pattern = get_link(dom, xpath_pattern, forum['url'], forum_posts)
    if url_xpath_pattern:
        result['url_xpath_pattern'] = url_xpath_pattern

    # add the post Date
    date_xpath_pattern = get_date(dom, xpath_pattern, forum['url'], forum_posts)
    if date_xpath_pattern:
        result['date_xpath_pattern'] = date_xpath_pattern

    # add the post user
    user_xpath_pattern = get_user(dom, xpath_pattern, forum['url'], forum_posts)
    if user_xpath_pattern:
        result['user_xpath_pattern'] = user_xpath_pattern
    return result
