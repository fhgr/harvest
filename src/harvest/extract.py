#!/usr/bin/env python3

'''
Extracts posts and metadata from Web forums based on the xpath's provide
by the machine learning component.

- posts are extracted "as is" and send through a boilerplate removal component
- URL and user metadata is extracted
- the post date is extracted based on the provided xpath + simple
  pre-processing
'''

from collections import namedtuple
from datetime import datetime
from operator import itemgetter
from urllib.parse import urljoin
from dateparser.search import search_dates

from harvest.utils import (get_html_dom, get_xpath_tree_text,
                           get_cleaned_element_text)
from harvest.cleanup.forum_post import remove_boilerplate

ExtractionResult = namedtuple('ExtractionResult', ('post', 'url', 'date',
                                                   'user'))


def _get_reference_url(url, element):
    '''
    Returns either the URL to the given element (if the `name` attribute is
    set) or the URL the element points to (if the `href` attribute is present).

    Args:
      element: The lxml element from which to extract the URL.

    Returns:
      str -- The URL that points to the element (name) or that the element
      is pointing to (href)
    '''
    if 'name' in element.attrib:
        return urljoin(url, "#{element.attrib['name']}")

    if 'href' in element.attrib:
        return urljoin(url, "{element.attrib['href']}")

    return None


def get_forum_date(dom, post_date_xpath):
    '''
    Selects the date present in the given post_date_xpath. Future dates are
    automatically filtered. If no date has been identified for a post, a None
    value is inserted.

    Args:
        dom: the DOM representation of the forum page.
        post_date_xpath (str): The xpath of the forum date.

    Returns:
        list -- A list of dates for every forum post.
    '''
    result = []
    date_mentions = (get_cleaned_element_text(e)
                     for e in dom.xpath(post_date_xpath))
    for date_mention in date_mentions:
        found = None
        for _, date in sorted(search_dates(date_mention),
                              key=itemgetter(1), reverse=True):
            if date <= datetime.now():
                found = date
                break
        result.append(found)

    return result


def get_forum_url(dom, url, post_url_xpath):
    '''
    Args:
      dom: The DOM representation of the forum page.
      post_url_xpath (str): The xpath to the post URL.
      url (str): The URL of the given page.

    Returns:
      list -- A list of all forum URLs.
    '''
    return [_get_reference_url(url, element)
            for element in dom.xpath(post_url_xpath)]


def generate_forum_url(url, num_posts):
    '''
    Generates forum URLs based on the forum base URL and the number of
    posts.

    Args:
      url (str): the forum URL
      num_posts (int): the number of posts for which to generate a URL
    Returns:
      list -- a list of URLs for the posts.
    '''
    return [urljoin(url, f'#{no}') for no in range(1, num_posts + 1)]


def extract_posts(html_content, url, post_xpath, post_url_xpath,
                  post_date_xpath, post_user_xpath):
    '''
    Returns:
      dict -- The extracted forum post and the corresponding metadat.
    '''
    dom = get_html_dom(html_content)

    forum_posts = remove_boilerplate(get_xpath_tree_text(dom, post_xpath))
    forum_urls = get_forum_url(dom, url, post_url_xpath) \
        if post_url_xpath else generate_forum_url(url, len(forum_posts))
    forum_dates = get_forum_date(dom, post_date_xpath) \
        if post_url_xpath else len(forum_posts) * ['']

    return [ExtractionResult(post, url, date, '')
            for post, url, date in zip(forum_posts, forum_urls, forum_dates)]
