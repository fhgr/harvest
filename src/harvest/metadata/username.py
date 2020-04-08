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

from harvest.utils import get_xpath_expression

USER_PAGE_HINTS = ('user', 'member', 'person', 'profile')


def get_user_name(name, base_url):
    '''
    returns
    -------
    A standardized representation of the user's URL.
    '''
    return ".".join(name.split()) + '@' + urlparse(base_url).netloc


def _get_regex_for_merged_classes(same_classes, xpath):
    same_classes_with_contains = ["contains(@class, \'" + x + "\')" for x in same_classes]
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
                    url_candidates[new_x_path]['is_merged'] = True


def _set_user_hint_exits(url_candidates):
    for xpath, matches in list(url_candidates.items()):
        for user_hint in USER_PAGE_HINTS:
            if re.search(user_hint, xpath, re.IGNORECASE):
                matches['contains_user_hint_class'] = True
                break
        for match in [m.get('href') for m in matches['elements']]:
            for user_hint in USER_PAGE_HINTS:
                if re.search(user_hint, match.lower(), re.IGNORECASE):
                    matches['contains_user_hint_href'] = True
                    break
            if matches['contains_user_hint_href']:
                break


# strategy
# --------
# * consider decendndants as well as elements at the same level
# * the number of URL candidates must be identical to the number of posts ;)
# * assign points for URLs that contain 'user', 'member', 'person', 'profile',
#   etc.


def get_user(dom, post_xpath, base_url, posts):
    '''
    Obtains the URL to the given post.

    Args:
        - dom: the forums DOM object
        - post_xpath: the determined post xpath
        - base url: URL of the given forum
        - posts: the extracted posts
    '''
    url_candidates = defaultdict(lambda: {'elements': [],
                                          'is_not_forum_path': True,
                                          'is_same_resource': True,
                                          'is_merged': False,
                                          'contains_user_hint_class': False,
                                          'contains_user_hint_href': False,
                                          'text_changes': False})
    post_elements = dom.xpath(post_xpath + "/..")

    # collect candidate paths
    for element in post_elements:
        for tag in element.iterdescendants():
            if tag.tag == 'a' and 'href' in tag.attrib:
                xpath = get_xpath_expression(tag)
                url_candidates[xpath]['elements'].append(tag)

    _merge_same_classes(url_candidates)

    # filter candidate paths
    for xpath, matches in list(url_candidates.items()):
        if len(matches['elements']) != len(posts):
            del url_candidates[xpath]

    _set_user_hint_exits(url_candidates)

    # Check if the text of the link changes
    for xpath, matches in list(url_candidates.items()):
        if len(np.unique([e.text for e in matches['elements'] if e.text])) > 1:
            matches['text_changes'] = True

    # filter candidates that contain URLs to other domains and
    # record the urls' targets
    forum_url = urlparse(base_url)
    for xpath, matches in list(url_candidates.items()):
        current_url_path = ''
        for match in matches['elements']:
            logging.info("Match attribs: %s of type %s.", match, type(match))
            parsed_url = urlparse(urljoin(base_url,
                                          match.attrib.get('href', '')))
            if parsed_url.netloc != forum_url.netloc:
                del url_candidates[xpath]
                break

            if not current_url_path:
                current_url_path = parsed_url.path

            if parsed_url.path == forum_url.path:
                url_candidates[xpath]['is_not_forum_path'] = False

            if parsed_url.path != current_url_path:
                url_candidates[xpath]['is_same_resource'] = False

    # obtain the most likely url path
    logging.info("%d rather than one URL candidate remaining. "
                 "Sorting candidates.", len(url_candidates))

    for xpath, _ in sorted(url_candidates.items(),
                           key=lambda x: (
                                   x[1]['is_not_forum_path'], x[1]['is_same_resource'], x[1]['text_changes'],
                                   x[1]['contains_user_hint_href'], x[1]['contains_user_hint_class'],
                                   x[1]['is_merged']), reverse=True):
        logging.info("Computed URL xpath for forum %s.", base_url)
        return xpath

    return None


def test_get_user_name():
    assert get_user_name('Therese Kurz', 'http://www.heise.de/security') == 'Therese.Kurz@www.heise.de'
