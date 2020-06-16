'''
Get the xpath to extract only the text of a post
'''
import re
import logging


def get_text_xpath_pattern(dom, post_xpath, posts):
    """
    Get the xpath to extract only the text of a post

    Args:
        - dom: the forums DOM object
        - post_xpath: the determined post xpath
        - posts: the extracted posts
    """

    text_xpath = re.sub(r"\/\.\.", "", post_xpath)
    while True:
        text_elements = dom.xpath(text_xpath)
        if len(text_elements) == len(posts):
            return text_xpath
        if len(text_elements) < len(posts) or len(text_elements) <= 1:
            logging.warning(f'text xPath not found for {post_xpath}')
            return post_xpath
        text_xpath = text_xpath + '/..'



