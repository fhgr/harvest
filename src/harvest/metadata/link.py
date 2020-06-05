'''
link
----

Tries to obtain the URL of the given post
'''
import logging
import re

from collections import defaultdict
from urllib.parse import urlparse, urljoin

from harvest.utils import get_xpath_expression, get_xpath_expression_child_filter, get_merged_xpath, extract_text


# strategy
# --------
# * consider decendndants as well as elements at the same level
# * the number of URL candidates must be identical to the number of posts ;)

def _get_link_representation(element):
    if extract_text(element):
        return extract_text(element)
    elif 'href' in element.attrib:
        return element.attrib['href']
    return ''


def _is_counting_up(candidates):
    for xpath, matches in candidates.items():
        post_ids = [re.search(r'\d+', _get_link_representation(x)) for x in matches['elements']]
        if all(post_ids):
            post_ids = [int(x.group(0)) for x in post_ids]
            if all(x < y for x, y in zip(post_ids, post_ids[1:])):
                matches['score'] += 1


def _get_link(dom, post_elements, base_url, forum_posts):
    '''
    Obtains the URL to the given post.
    '''
    url_candidates = defaultdict(lambda: {'elements': [],
                                          'has_anchor_tag': False, 'score': 0})

    # collect candidate paths
    for element in post_elements:
        for tag in element.iterdescendants():
            if tag.tag == 'a':
                xpath = get_xpath_expression(tag)
                xpath += get_xpath_expression_child_filter(tag)
                # anchor tags with the name attribute will
                # lead to the post
                attributes = list(attr.lower() for attr in tag.attrib)
                if 'name' in attributes:
                    url_candidates[xpath]['has_anchor_tag'] = True
                if 'name' in attributes or 'href' in attributes:
                    url_candidates[xpath]['elements'].append(tag)

    # merge xpath
    for merged_xpath in get_merged_xpath(url_candidates.keys()):
        merged_elements = dom.xpath(merged_xpath)
        if merged_elements:
            url_candidates[merged_xpath]['elements'] = merged_elements
            if 'name' in (attr.lower() for attr in merged_elements[0].attrib):
                url_candidates[merged_xpath]['has_anchor_tag'] = True

    # filter candidate paths
    for xpath, matches in list(url_candidates.items()):
        # consider the number of posts or the number of posts + 2 spare for possible header elements
        if len(forum_posts) - len(matches['elements']) not in range(0, 3):
            del url_candidates[xpath]

    # filter candidates that contain URLs to other domains and
    # record the urls' targets
    forum_url = urlparse(base_url)
    for xpath, matches in list(url_candidates.items()):
        current_url_path = ''
        for match in matches['elements']:
            parsed_url = urlparse(urljoin(base_url,
                                          match.attrib.get('href', '')))
            if parsed_url.netloc != forum_url.netloc:
                del url_candidates[xpath]
                break

            if not current_url_path:
                current_url_path = parsed_url.path

            if parsed_url.path != forum_url.path or parsed_url.path != current_url_path:
                del url_candidates[xpath]
                break

    _is_counting_up(url_candidates)

    # obtain the most likely url path
    for xpath, _ in sorted(url_candidates.items(),
                           key=lambda x: (x[1]['has_anchor_tag'], x[1]['score']),
                           reverse=True):
        return xpath

    return None


def get_link(dom, post_xpath, base_url, forum_posts):
    '''
    Args:
        dom: The DOM tree to analyze.
        post_xpath (str): xpath of the post to search dates.
        base_url (str): URL of the forum.
    Returns:
        str: the xpath to the post date.
    '''

    logging.info('Start finding post link')
    post_elements = dom.xpath(post_xpath)
    while True:
        result = _get_link(dom, post_elements, base_url, forum_posts)
        if result or len(post_elements) <= 1:
            logging.info(f'Post link xpath: {result}')
            return result
        post_xpath = post_xpath + "/.."
        post_elements = dom.xpath(post_xpath)