'''
link
----

Tries to obtain the name of the post's author
'''
import logging
import re
import numpy as np

from collections import defaultdict
from urllib.parse import urlparse, urljoin

from harvest.utils import get_xpath_expression, get_xpath_expression_child_filter

USER_PAGE_HINTS = ('user', 'member', 'person', 'profile')
FORBIDDEN_TERMS = ('terms of use', 'privacy policy', 'add message', 'reply', 'answer', 'share', 'report')

SCORE_INCREMENT = 1
SCORE_TEXT_CHANCE_INCREMENT = 3


def get_user_name(name, base_url):
    '''
    returns
    -------
    A standardized representation of the user's URL.
    '''
    return ".".join(name.split()) + '@' + urlparse(base_url).netloc


def _get_regex_for_merged_classes(same_classes, xpath):
    same_classes_with_contains = ["contains(@class, \'" + x + "\')" for x in same_classes]
    same_classes_with_contains.sort()
    return re.sub(r"\/\/a\[@class=\"[\d\w\s]*\"\]", "//a[" + " and ".join(same_classes_with_contains) + "]", xpath)


def _append_merged_url_candidates(url_candidates, new_x_path, matches):
    for element in [m for m in matches['elements'] if
                    m not in url_candidates[new_x_path]['elements']]:
        url_candidates[new_x_path]['elements'].append(element)


def _merge_same_classes(url_candidates):
    candidates_to_check = [c for c in list(url_candidates.items()) if
                           c[1]['elements'] and c[1]['elements'][0].attrib.get('class')]
    for xpath, matches in candidates_to_check:
        for xpathToCompare, matchesToCompare in [c for c in candidates_to_check if c[0] != xpath]:
            html_class = matches['elements'][0].attrib.get('class').split(" ")
            html_class_to_compare = matchesToCompare['elements'][0].attrib.get('class').split(" ")
            same_classes = list(set(html_class).intersection(html_class_to_compare))
            if same_classes:
                new_x_path = _get_regex_for_merged_classes(same_classes, xpath)
                new_x_path_to_compare = _get_regex_for_merged_classes(same_classes, xpathToCompare)
                if new_x_path == new_x_path_to_compare:
                    _append_merged_url_candidates(url_candidates, new_x_path, matches)
                    _append_merged_url_candidates(url_candidates, new_x_path, matchesToCompare)


def _set_user_hint_exits_for_attribute(matches, attribute_value):
    for user_hint in USER_PAGE_HINTS:
        if re.search(user_hint, attribute_value, re.IGNORECASE):
            matches['score'] += SCORE_INCREMENT
            return True


def _set_user_hint_exits(url_candidates):
    for xpath, matches in list(url_candidates.items()):
        _set_user_hint_exits_for_attribute(matches, xpath)
        for match in [m.get('href') for m in matches['elements']]:
            if _set_user_hint_exits_for_attribute(matches, match.lower()):
                break


def _set_text_changes(url_candidates):
    for xpath, matches in list(url_candidates.items()):
        if len(np.unique([e.text for e in matches['elements'] if e.text])) > 1:
            matches['score'] += SCORE_TEXT_CHANCE_INCREMENT
        else:
            text_in_sub_elements = []
            for tag in [e for e in matches['elements']]:
                for subTag in tag.iterdescendants('span', 'div', 'b', 'strong'):
                    if subTag.text and subTag.text not in text_in_sub_elements:
                        text_in_sub_elements.append(subTag.text)
            if len(text_in_sub_elements) > 1:
                matches['score'] += SCORE_TEXT_CHANCE_INCREMENT


def _remove_items_with_forbidden_words(url_candidates):
    for xpath, matches in list(url_candidates.items()):
        for tag in matches['elements']:
            if tag.text and tag.text.lower() in FORBIDDEN_TERMS:
                del url_candidates[xpath]
                break


# strategy
# --------
# * consider decendndants as well as elements at the same level
# * the number of URL candidates must be identical to the number of posts
#   or must not have less than two elements than the posts
# * assign points for URLs that contain 'user', 'member', 'person', 'profile',
#   etc.


def get_user(dom, post_xpath, base_url, posts):
    """
    Obtains the URL to the given post.

    Args:
        - dom: the forums DOM object
        - post_xpath: the determined post xpath
        - base url: URL of the given forum
        - posts: the extracted posts
    """
    url_candidates = defaultdict(lambda: {'elements': [], 'score': 0})
    post_elements = dom.xpath(post_xpath + "/..")

    # collect candidate paths
    for element in post_elements:
        for tag in element.iterdescendants():
            if tag.tag == 'a' and 'href' in tag.attrib:
                xpath = get_xpath_expression(tag)
                xpath += get_xpath_expression_child_filter(tag)
                url_candidates[xpath]['elements'].append(tag)

    _merge_same_classes(url_candidates)

    # filter candidate paths
    for xpath, matches in list(url_candidates.items()):
        if len(matches['elements']) > len(posts) or len(matches['elements']) < len(posts) - 2:
            del url_candidates[xpath]

    _remove_items_with_forbidden_words(url_candidates)

    _set_user_hint_exits(url_candidates)

    _set_text_changes(url_candidates)

    # filter candidates that contain URLs to other domains and
    # record the urls' targets
    forum_url = urlparse(base_url)
    for xpath, matches in list(url_candidates.items()):
        for match in matches['elements']:
            logging.info("Match attribs: %s of type %s.", match, type(match))
            parsed_url = urlparse(urljoin(base_url, match.attrib.get('href', '')))
            if parsed_url.netloc and parsed_url.netloc != forum_url.netloc or parsed_url.path == forum_url.path:
                del url_candidates[xpath]
                break

    # obtain the most likely url path
    logging.info("%d rather than one URL candidate remaining. "
                 "Sorting candidates.", len(url_candidates))

    for xpath, _ in sorted(url_candidates.items(),
                           key=lambda x: (x[1]['score']), reverse=True):
        logging.info("Computed URL xpath for forum %s.", base_url)
        return xpath

    return None
