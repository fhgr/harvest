'''
link
----

Tries to obtain the URL of the given post
'''
import logging

from collections import defaultdict
from urllib.parse import urlparse, urljoin

from harvest.utils import get_xpath_expression, get_xpath_expression_child_filter, get_merged_xpath


# strategy
# --------
# * consider decendndants as well as elements at the same level
# * the number of URL candidates must be identical to the number of posts ;)

def get_link(dom, post_xpath, base_url, forum_posts):
    '''
    Obtains the URL to the given post.
    '''
    url_candidates = defaultdict(lambda: {'elements': [],
                                          'has_anchor_tag': False})

    # post elements contains less elements than forum_posts (!)
    # since it takes the container with the posts
    post_elements = dom.xpath(post_xpath + "/..")

    # collect candidate paths
    for element in post_elements:
        for tag in element.iterdescendants():
            if tag.tag == 'a':
                xpath = get_xpath_expression(tag)
                xpath += get_xpath_expression_child_filter(tag)
                # anchor tags with the name attribute will
                # lead to the post
                if 'name' in (attr.lower() for attr in tag.attrib):
                    logging.info("Computed URL xpath for forum %s.", base_url)
                    url_candidates[xpath]['has_anchor_tag'] = True

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
            logging.info("Match attribs: %s of type %s.", match, type(match))
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

    # obtain the most likely url path
    logging.info("%d rather than one URL candidate remaining. "
                 "Sorting candidates.", len(url_candidates))
    for xpath, _ in sorted(url_candidates.items(),
                           key=lambda x: (x[1]['has_anchor_tag']),
                           reverse=True):
        logging.info("Computed URL xpath for forum %s.", base_url)
        return xpath

    return None
