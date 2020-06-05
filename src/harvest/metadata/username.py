'''
link
----

Tries to obtain the name of the post's author
'''
import logging
import re
import numpy as np

from harvest.config import LANGUAGES
from itertools import combinations
from collections import defaultdict
from dateparser.search import search_dates
from urllib.parse import urlparse, urljoin

from harvest.utils import (get_xpath_expression, get_xpath_expression_child_filter, get_merged_xpath,
                           get_cleaned_element_text)

USER_PAGE_HINTS = ('user', 'member', 'person', 'profile')
FORBIDDEN_TERMS = ('terms of use', 'privacy policy', 'add message', 'reply', 'answer', 'share', 'report', 'registered',
                   'setting')

SCORE_INCREMENT = 1
SCORE_TEXT_CHANCE_INCREMENT = 3


def _set_user_hint_exits_for_attribute(matches, attribute_value):
    for user_hint in USER_PAGE_HINTS:
        if re.search(user_hint, attribute_value, re.IGNORECASE):
            matches['score'] += SCORE_INCREMENT
            return True


def _set_user_hint_exits(url_candidates):
    for xpath, matches in [x for x in url_candidates.items()]:
        _set_user_hint_exits_for_attribute(matches, xpath)
        for match in [m.get('href') for m in matches['elements'] if m.get('href')]:
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


def _filter_items_with_forbidden_words(url_candidates):
    for xpath, matches in list(url_candidates.items()):
        for tag in matches['elements']:
            if tag.text and tag.text.strip().lower() in FORBIDDEN_TERMS:
                del url_candidates[xpath]
                break


def _filter_user_name_without_link_includes_date(url_candidates):
    for xpath, candidate in [x for x in url_candidates.items() if not x[1]['is_link']]:
        for element in candidate['elements']:
            text = element.text.strip()
            if search_dates(text, languages=LANGUAGES) or text in FORBIDDEN_TERMS:
                del url_candidates[xpath]
                break


def _filter_user_name_without_link_and_no_text_changes(url_candidates):
    for xpath, candidate in [x for x in url_candidates.items()
                             if not x[1]['is_link'] and x[1]['score'] == 0]:
        previous_element = None
        has_changed = False
        for element in candidate['elements']:
            text = element.text.strip()
            if previous_element is not None and previous_element.text.strip() != text:
                has_changed = True
                break
            previous_element = element

        if not has_changed and url_candidates[xpath]:
            del url_candidates[xpath]


def _filter_more_than_one_element_per_post(url_candidates, post_elements):
    if len(post_elements) > 1:
        for xpath, candidate in [x for x in url_candidates.items()]:
            for post_element in post_elements:
                if len([x for x in post_element.iterdescendants() if x in candidate['elements']]) > 1 and \
                        url_candidates[xpath]:
                    del url_candidates[xpath]
                    break


def _filter_post_links(url_candidates):
    for xpath, candidate in list(url_candidates.items()):
        sequence = re.findall(r"\d+", " ".join(get_cleaned_element_text(x) for x in candidate['elements']))
        sequence = [int(s) for s in sequence]
        if len(sequence) > 2 and all(x + 1 == y for x, y in zip(sequence, sequence[1:])):
            del url_candidates[xpath]


def _filter_post_to_candidate_length(url_candidates, posts):
    for xpath, matches in list(url_candidates.items()):
        if len(matches['elements']) > len(posts) or len(matches['elements']) < len(posts) - 2:
            del url_candidates[xpath]


def _filter_url_other_domain(url_candidates, base_url):
    forum_url = urlparse(base_url)
    for xpath, matches in [x for x in url_candidates.items() if x[1]['is_link']]:
        for match in matches['elements']:
            parsed_url = urlparse(urljoin(base_url, match.attrib.get('href', '')))
            if parsed_url.netloc and parsed_url.netloc != forum_url.netloc or parsed_url.path == forum_url.path:
                del url_candidates[xpath]
                break


def _is_user_name_pattern(text):
    return text and text.strip() and 3 < len(text.strip()) < 100 and len(
        text.strip().split(" ")) <= 4 and not re.findall('http[s]?://', text)


def _contains_user_name_pattern(tag):
    if tag.getchildren():
        return _is_user_name_pattern(" ".join([get_cleaned_element_text(x) for x in tag.iterdescendants()]))
    return _is_user_name_pattern(tag.text)


def _combine_xpath_candidates(url_candidates, number_of_posts):
    candidates_less_then_posts = [x for x in url_candidates.items() if len(x[1]['elements']) < number_of_posts]
    if number_of_posts > 1 and len(candidates_less_then_posts) > 1:
        valid_combinations = []
        for comb in combinations(candidates_less_then_posts, 2):
            if len(comb[0][1]['elements']) + len(comb[1][1]['elements']) == number_of_posts:
                valid_combinations.append(comb)
        for elements1, elements2 in sorted(valid_combinations,
                                           key=lambda x: (x[0][1]['score'] + x[1][1]['score']), reverse=True):
            combined_xpath = elements1[0] + "|" + elements2[0]
            url_candidates[combined_xpath]['elements'] = elements1[1]['elements'] + elements2[1]['elements']
            url_candidates[combined_xpath]['is_link'] = elements1[1]['is_link'] or elements2[1]['is_link']
            url_candidates[combined_xpath]['score'] = min(elements1[1]['score'], elements2[1]['score'])
            break


def _collect_candidates_paths(post_elements):
    url_candidates = defaultdict(lambda: {'elements': [], 'is_link': True, 'score': 0})
    for element in post_elements:
        for tag in element.iterdescendants():
            if ((tag.tag == 'a' and 'href' in tag.attrib and not [x for x in list(tag) if x.tag == 'time']) or
                (tag.tag in ['span', 'strong', 'div', 'b'] and not list(tag))) and \
                    _contains_user_name_pattern(tag):
                xpath = get_xpath_expression(tag, parent_element=element, single_class_filter=True)
                xpath += get_xpath_expression_child_filter(tag)
                url_candidates[xpath]['elements'].append(tag)
                if tag.tag != 'a':
                    url_candidates[xpath]['is_link'] = False

    return url_candidates


def get_user_name(name, base_url):
    '''
    returns
    -------
    A standardized representation of the user's URL.
    '''
    return ".".join(name.split()) + '@' + urlparse(base_url).netloc


def _get_user(dom, post_elements, base_url, posts):
    url_candidates = _collect_candidates_paths(post_elements)

    for merged_xpath in get_merged_xpath(url_candidates.keys()):
        merged_elements = dom.xpath(merged_xpath)
        if merged_elements:
            url_candidates[merged_xpath]['elements'] = merged_elements

    _filter_url_other_domain(url_candidates, base_url)
    _filter_items_with_forbidden_words(url_candidates)
    _filter_user_name_without_link_includes_date(url_candidates)
    _filter_post_links(url_candidates)
    _filter_more_than_one_element_per_post(url_candidates, post_elements)

    _set_user_hint_exits(url_candidates)
    _set_text_changes(url_candidates)

    _combine_xpath_candidates(url_candidates, len(posts))
    _filter_user_name_without_link_and_no_text_changes(url_candidates)

    _filter_post_to_candidate_length(url_candidates, posts)

    # obtain the most likely url path

    for xpath, _ in sorted(url_candidates.items(),
                           key=lambda x: (x[1]['is_link'], x[1]['score'], len(x[1]['elements'])), reverse=True):
        return xpath

    return None


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
    logging.info('Start finding user name')
    post_elements = dom.xpath(post_xpath)
    while True:
        result = _get_user(dom, post_elements, base_url, posts)
        if result or len(post_elements) <= 1:
            logging.info(f'User name xpath: {result}')
            return result
        post_xpath = post_xpath + "/.."
        post_elements = dom.xpath(post_xpath)
