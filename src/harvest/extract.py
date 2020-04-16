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
from dateutil import parser

from harvest.utils import (get_html_dom, get_xpath_tree_text, get_cleaned_element_text, get_xpath_expression,
                           get_xpath_expression_child_filter)

from harvest.cleanup.forum_post import remove_boilerplate, remove_first_none_posts

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
        return urljoin(url, f"#{element.attrib['name']}")

    if 'href' in element.attrib:
        return urljoin(url, f"{element.attrib['href']}")

    return None


def _get_date_text(time_element):
    if time_element.tag == 'time' and 'datetime' in time_element.attrib:
        time = time_element.attrib.get('datetime', '')
        parsed_time = parser.parse(time, ignoretz=True)
        return parsed_time.ctime()
    else:
        return get_cleaned_element_text(time_element)


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
    date_mentions = (_get_date_text(e)
                     for e in dom.xpath(post_date_xpath) if search_dates(_get_date_text(e)))
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


def get_same_number_of_url_as_posts(length_forum_post, forum_urls):
    result = forum_urls[:]
    if len(forum_urls) != length_forum_post and len(forum_urls) == 1:
        for x in range(0, length_forum_post - 1):
            result.append(forum_urls[0])
    return result


def add_anonymous_user(dom, users, post_xpath, post_user_xpath):
    posts = dom.xpath(post_xpath)
    if len(posts) > len(users):
        for index in range(len(posts)):
            contains_user = False
            for tag in posts[index].iterdescendants():
                if tag.tag == 'a' and 'href' in tag.attrib:
                    xpath = get_xpath_expression(tag)
                    xpath += get_xpath_expression_child_filter(tag)
                    if post_user_xpath == xpath:
                        contains_user = True
                        break
            if not contains_user:
                users.insert(index, "Anonymous")
                if len(posts) == len(users):
                    break


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
        if post_date_xpath else len(forum_posts) * ['']
    forum_users = get_forum_url(dom, url, post_user_xpath) \
        if post_user_xpath else len(forum_posts) * ['']

    add_anonymous_user(dom, forum_users, post_xpath, post_user_xpath)
    # forum_posts = remove_first_none_posts(forum_posts, forum_users)
    forum_urls = get_same_number_of_url_as_posts(len(forum_posts), forum_urls)
    print("****", forum_users)

    return [ExtractionResult(post, url, date, user)
            for post, url, date, user in zip(forum_posts, forum_urls,
                                             forum_dates, forum_users)]
