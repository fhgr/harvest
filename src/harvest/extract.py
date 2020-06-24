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
from urllib.parse import urljoin, urlparse
from dateparser.search import search_dates
from dateutil import parser

from harvest.utils import get_html_dom, get_xpath_tree_text, get_cleaned_element_text, extract_text

from harvest.cleanup.forum_post import remove_boilerplate
from harvest.config import LANGUAGES

ExtractionResult = namedtuple('ExtractionResult', ('post', 'url', 'date',
                                                   'user'))


def _get_reference_url(element):
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
        return f"#{element.attrib['name']}"

    if 'href' in element.attrib:
        return f"{element.attrib['href']}"

    return None


def _get_user_name(element):
    '''
    Returns either the URL to the given element (if the `name` attribute is
    set) or the URL the element points to (if the `href` attribute is present) or the cleaned text.

    Args:
      element: The lxml element from which to extract the URL.

    Returns:
      str -- The URL that points to the element (name) or that the element
      is pointing to (href)
    '''
    if element.tag == 'a':
        return _get_reference_url(element)
    else:
        return extract_text(element)


def _get_date_text(time_element, time_element_as_datetime=True):
    is_tag_time = time_element.tag == 'time'
    if is_tag_time and 'datetime' in time_element.attrib:
        if time_element_as_datetime:
            time = time_element.attrib.get('datetime', '')
            parsed_time = parser.parse(time, ignoretz=True)
            return is_tag_time, parsed_time

    return is_tag_time, get_cleaned_element_text(time_element)


def get_forum_date(dom, post_date_xpath, result_as_datetime=True):
    '''
    Selects the date present in the given post_date_xpath. Future dates are
    automatically filtered. If no date has been identified for a post, a None
    value is inserted.

    Args:
        dom: the DOM representation of the forum page.
        post_date_xpath (str): The xpath of the forum date.
        result_as_datetime (bool): If true the date are returned as datetime. Otherwise the date are returned as string

    Returns:
        list -- A list of dates for every forum post.
    '''
    result = []
    date_mentions = (_get_date_text(e, time_element_as_datetime=result_as_datetime)
                     for e in dom.xpath(post_date_xpath) if
                     e.tag == 'time' or search_dates(_get_date_text(e)[1], languages=LANGUAGES))
    for is_time_element, date_mention in date_mentions:
        found = None
        if is_time_element:
            found = date_mention
        else:
            for data_as_string, date in sorted(
                    search_dates(date_mention, settings={'RETURN_AS_TIMEZONE_AWARE': False}, languages=LANGUAGES),
                    key=itemgetter(1), reverse=True):
                if date <= datetime.now():
                    if result_as_datetime:
                        found = date
                    else:
                        found = data_as_string
                    break
        result.append(found)

    return result


def get_forum_url(dom, post_url_xpath):
    '''
    Args:
      dom: The DOM representation of the forum page.
      post_url_xpath (str): The xpath to the post URL.
      url (str): The URL of the given page.

    Returns:
      list -- A list of all forum URLs.
    '''
    return [_get_reference_url(element)
            for element in dom.xpath(post_url_xpath)]


def get_forum_user(dom, post_user_xpath):
    '''
    Args:
      dom: The DOM representation of the forum page.
      post_user_xpath (str): The xpath to the post user name.
      url (str): The URL of the given page.

    Returns:
      list -- A list of all forum URLs.
    '''
    return [_get_user_name(element)
            for element in dom.xpath(post_user_xpath)]


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


def _get_same_size_as_posts(length_forum_post, forum_element):
    result = forum_element[-length_forum_post:]
    if len(forum_element) != length_forum_post:
        for x in range(0, length_forum_post - len(forum_element)):
            result.append(forum_element[0])
    return result


def _get_container_elements(dom, xpath, number_of_posts):
    post_elements = dom.xpath(xpath)
    while True:
        xpath = xpath + "/.."
        new_post_elements = dom.xpath(xpath)
        if new_post_elements is None or len(new_post_elements) < number_of_posts:
            return post_elements
        post_elements = new_post_elements


def add_anonymous_user(dom, users, post_xpath, post_user_xpath):
    posts = dom.xpath(post_xpath)
    if len(posts) > len(users):
        user_elements = dom.xpath(post_user_xpath)
        posts = _get_container_elements(dom, post_xpath, len(posts))
        for index in range(len(posts)):
            contains_user = False
            for tag in posts[index].iterdescendants():
                if tag in user_elements:
                    contains_user = True
                    break
            if not contains_user:
                users.insert(index, "Anonymous")
                if len(posts) == len(users):
                    break


def extract_posts(html_content, url, post_xpath, post_url_xpath,
                  post_date_xpath, post_user_xpath, result_as_datetime=True):
    '''
    Returns:
      dict -- The extracted forum post and the corresponding metadat.
    '''
    dom = get_html_dom(html_content)

    forum_posts = remove_boilerplate(get_xpath_tree_text(dom, post_xpath))
    forum_urls = get_forum_url(dom, post_url_xpath) \
        if post_url_xpath else generate_forum_url(url, len(forum_posts))
    forum_dates = get_forum_date(dom, post_date_xpath, result_as_datetime=result_as_datetime) \
        if post_date_xpath else len(forum_posts) * ['']
    forum_users = get_forum_user(dom, post_user_xpath) \
        if post_user_xpath else len(forum_posts) * ['']

    add_anonymous_user(dom, forum_users, post_xpath, post_user_xpath)
    forum_urls = _get_same_size_as_posts(len(forum_posts), forum_urls)
    forum_dates = _get_same_size_as_posts(len(forum_posts), forum_dates)
    forum_users = _get_same_size_as_posts(len(forum_posts), forum_users)

    return [ExtractionResult(post, url, date, user)
            for post, url, date, user in zip(forum_posts, forum_urls,
                                             forum_dates, forum_users)]
