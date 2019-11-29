'''
link
----

Tries to obtain the URL of the given post
'''
import logging

from collections import defaultdict
from urllib.parse import urlparse

from harvest.utils import get_xpath_expression


# strategy
# --------
# * the number of URL candidates must be identical to the number of posts ;)

def get_link(dom, post_xpath, base_url):
    '''
    Obtains the URL to the given post.
    '''
    url_candidates = defaultdict(lambda: {'elements': [],
                                          'is_forum_path': True,
                                          'is_same_resource': True})
    post_elements = dom.xpath(post_xpath)

    # collect candidate paths
    for element in post_elements:
        for tag in element.iterdescendants():
            if tag.tag == 'a':
                xpath = get_xpath_expression(tag)
                # anchor tags with the name attribute will
                # lead to the post
                if 'name' in tag.attrib:
                    return xpath

                url_candidates[xpath]['elements'].append(tag)

    # filter candidate paths
    for xpath, matches in list(url_candidates.items()):
        if len(matches['elements']) != len(post_elements):
            del url_candidates[xpath]

    # filter candidates that contain URLs to other domains and
    # record the urls' targets
    forum_url = urlparse(base_url)
    for xpath, matches in list(url_candidates.items()):
        current_url_path = ''
        for match in matches:
            parsed_url = urlparse(match.attrib.get('href', ''))
            if parsed_url.netloc != forum_url.netloc:
                del url_candidates[xpath]
                break

            if not current_url_path:
                current_url_path = parsed_url.path

            if parsed_url.path != forum_url.path:
                url_candidates[xpath]['is_forum_path'] = False

            if parsed_url.path != current_url_path:
                url_candidates[xpath]['is_same_resource'] = False

    # obtain the most likely url path
    logging.info("%d rather than one URL candidate remaining. "
                 "Sorting candidates.", len(url_candidates))
    for xpath, _ in sorted(url_candidates.items(),
                           key=lambda x: (x[1][1], x[1][2]),
                           reversed=True):
        return xpath

    return None
