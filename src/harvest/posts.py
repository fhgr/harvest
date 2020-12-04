#!/usr/bin/env python3

# Forum Extraction AI and heuristic
# ---------------------------------
# (C)opyrights 2020 Albert Weichselbraun

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

# cleanup posts
# -------------
# * remove repeated elements
# * appear at the beginning or end of a post
# * may contain information on
#   - user
#   - date (subscription versus post date) => always compare dates within a page for computing the date extraction rule
#   - replies, likes, etc.

import logging
import re

from lxml import etree

from harvest.cleanup.forum_post import remove_boilerplate
from harvest.metadata.date import get_date
from harvest.metadata.link import get_link
from harvest.metadata.username import get_user
from harvest.metadata.usertext import get_text_xpath_pattern
from harvest.post_text import get_cleaned_text
from harvest.similarity_calculator import assess_node
from harvest.utils import (get_xpath_expression, get_html_dom, get_xpath_combinations_for_classes,
                           get_xpath_tree_text, get_grandparent, elements_have_no_overlap)

CORPUS = "./data/forum/"

# number of characters required for a match
MATCH_PREFIX_SIZE = 30

BLACKLIST_POST_TEXT_TAG = ('h1', 'h2', 'h3', 'h4', 'h5', 'a')

# minimum number of posts we suspect on the page
MIN_POST_COUNT = 3


def _get_matching_element(comment, dom):
    """
    returns
    -------
    the element that matches the given comment
    """
    if not comment.strip():
        return None

    for e in dom.iter():
        text = (e.text or "").strip()
        min_length_of_text = len(comment[:MATCH_PREFIX_SIZE])
        if text and comment.startswith(text[:MATCH_PREFIX_SIZE]) and len(text) >= min_length_of_text and \
                e.tag is not etree.Comment:
            return e

    return None


def _get_xpath_tree(comment, dom, tree):
    element = _get_matching_element(comment, dom)
    return (None, None) if element is None else (element, tree.getpath(element))


def _remove_trailing_p_element(xpath_score, xpath_element_count, xpath, reference_text, dom):
    """
    The p elements at the end can be removed. Some posts have several p elements and some have none at all.
    Those without p element can then not be detected. As Example, leading post can not be detected:
    https://us.forums.blizzard.com/en/wow/t/layers-and-character-creation-adjustments-on-select-realms/499760

    Args:
        xpath: the xpath to remove the p element from

    Returns:

    """
    cleaned_xpath = re.sub(r'(?<!([\/]))\/p$', '', xpath)
    if cleaned_xpath != xpath:
        xpath_score, xpath_element_count = assess_node(reference_content=reference_text, dom=dom,
                                                       xpath=cleaned_xpath)
    return xpath_score, xpath_element_count, cleaned_xpath


def _get_xpaths_candidates(text_sections, dom, tree, reference_text):
    candidate_xpaths = []
    for section_text in text_sections:
        element, xpath = _get_xpath_tree(section_text, dom, tree)
        logging.debug(f"Processing section of text '{section_text}' with xpath '{xpath}'.")
        if not xpath:
            continue
        element = _get_matching_element(section_text, dom)
        if element.tag not in BLACKLIST_POST_TEXT_TAG:
            xpath_pattern = get_xpath_expression(element, parent_element=get_grandparent(element),
                                                 single_class_filter=True)

            xpath_score, xpath_element_count = assess_node(reference_content=reference_text, dom=dom,
                                                           xpath=xpath_pattern, reward_classes=True)
            if xpath_element_count > 1:
                candidate_xpaths.append((xpath_score, xpath_element_count, xpath_pattern))

    return candidate_xpaths


def _get_entire_post(xpath_pattern, xpath_score, reference_text, dom):
    while True:
        new_xpath_pattern = xpath_pattern + "/.."
        new_xpath_score, new_xpath_element_count = assess_node(reference_content=reference_text, dom=dom,
                                                               xpath=new_xpath_pattern)
        if new_xpath_element_count < MIN_POST_COUNT:
            return xpath_pattern, xpath_score

        xpath_pattern = new_xpath_pattern
        xpath_score = new_xpath_score


def _get_combination_of_posts(xpath_pattern, xpath_score, xpath_element_count, reference_text, dom):
    """
    Check if combinations of classes result in detecting leading post
    Args:
        xpath_pattern:
        xpath_score:
        xpath_element_count:
        reference_text:
        dom:

    Returns:
    Combination of classes if they resulting in a better score. Otherwise the parameters xpath_patter, xpath_score and
    xpath_element_count are returned.
    """
    candidate_xpaths = []
    for final_xpath in get_xpath_combinations_for_classes(xpath_pattern):
        new_xpath_score, new_xpath_element_count = assess_node(reference_content=reference_text, dom=dom,
                                                               xpath=final_xpath)
        if (xpath_element_count < new_xpath_element_count <= xpath_element_count + 2 or
            xpath_element_count * 2 - new_xpath_element_count in range(-1, 2)) and new_xpath_score > xpath_score:
            if elements_have_no_overlap(dom.xpath(final_xpath)):
                candidate_xpaths.append((new_xpath_score, new_xpath_element_count, final_xpath))

    if candidate_xpaths:
        candidate_xpaths.sort()
        return candidate_xpaths.pop()
    return xpath_score, xpath_element_count, xpath_pattern


def extract_posts(html, url):
    dom = get_html_dom(html)
    tree = etree.ElementTree(dom)
    result = {'url': url, 'dragnet': None, 'url_xpath_pattern': None, 'xpath_pattern': None,
              'xpath_score': None, 'forum_posts': None, 'date_xpath_pattern': None, 'user_xpath_pattern': None,
              'text_xpath_pattern': None}

    text_sections = get_cleaned_text(html)
    logging.debug(f"Extracted {len(text_sections)} lines of comments.")
    reference_text = " ".join(text_sections)

    candidate_xpaths = _get_xpaths_candidates(text_sections, dom, tree, reference_text)

    if not candidate_xpaths:
        logging.warning("Couldn't identify any candidate posts for forum", url)
        return result

    # obtain anchor node
    candidate_xpaths.sort()
    xpath_score, xpath_element_count, xpath_pattern = candidate_xpaths.pop()
    xpath_score, xpath_element_count, xpath_pattern = _remove_trailing_p_element(xpath_score, xpath_element_count,
                                                                                 xpath_pattern, reference_text, dom)

    xpath_pattern, xpath_score = _get_entire_post(xpath_pattern, xpath_score, reference_text, dom)

    xpath_score, xpath_element_count, xpath_pattern = _get_combination_of_posts(xpath_pattern, xpath_score,
                                                                                xpath_element_count, reference_text,
                                                                                dom)

    logging.info(
        f"Obtained most likely forum xpath for forum {url}: {xpath_pattern} with a score of {xpath_score}.")
    if xpath_pattern:
        forum_posts = get_xpath_tree_text(dom, xpath_pattern)
        forum_posts = remove_boilerplate(forum_posts)

    result['xpath_pattern'] = xpath_pattern
    result['xpath_score'] = xpath_score
    result['forum_posts'] = forum_posts

    if xpath_pattern:
        result['text_xpath_pattern'] = get_text_xpath_pattern(dom, xpath_pattern, forum_posts)

    # add the post URL
    url_xpath_pattern = get_link(dom, xpath_pattern, url, forum_posts)
    if url_xpath_pattern:
        result['url_xpath_pattern'] = url_xpath_pattern

    # add the post Date
    date_xpath_pattern = get_date(dom, xpath_pattern, url, forum_posts)
    if date_xpath_pattern:
        result['date_xpath_pattern'] = date_xpath_pattern

    # add the post user
    user_xpath_pattern = get_user(dom, xpath_pattern, url, forum_posts)
    if user_xpath_pattern:
        result['user_xpath_pattern'] = user_xpath_pattern
    return result
