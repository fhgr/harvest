'''
link
----

Tries to obtain the name of the post's author
'''
import logging

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
                                          'is_forum_path': True,
                                          'is_same_resource': True})
    post_elements = dom.xpath(post_xpath + "/..")

    # collect candidate paths
    for element in post_elements:
        for tag in element.iterdescendants():
            if tag.tag == 'a' and 'href' in tag.attrib:
                xpath = get_xpath_expression(tag)
                url_candidates[xpath]['elements'].append(tag)

    # filter candidate paths
    for xpath, matches in list(url_candidates.items()):
        if len(matches['elements']) != len(posts):
            del url_candidates[xpath]

    # filter candidates that contain URLs to other domains and
    # record the urls' targets
    forum_url = urlparse(base_url)
    for xpath, matches in list(url_candidates.items()):
        current_url_path = ''
        for match in matches['elements']:
            logging.info("Match attribs: %s of type %s.", match, type(match))
            logging.info(match.tag + ">" + str(match.attrib))
            parsed_url = urlparse(urljoin(base_url,
                                          match.attrib.get('href', '')))
            if parsed_url.netloc != forum_url.netloc:
                print("DDEL", parsed_url.netloc,">F", forum_url.netloc)
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
                           key=lambda x: (x[1]['is_forum_path'], x[1]['is_same_resource']),
                           reverse=True):
        logging.info("Computed URL xpath for forum %s.", base_url)
        return xpath

    return None

def test_get_user_name():
    assert get_user_name('Therese Kurz', 'http://www.heise.de/security') == 'Therese.Kurz@www.heise.de'
