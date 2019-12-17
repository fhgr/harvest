'''
Functions that are shared across modules.
'''

import re
from lxml import etree

VALID_NODE_TYPE_QUALIFIERS = ('class', )
RE_FILTER_XML_HEADER = re.compile("<\\?xml version=\".*? encoding=.*?\\?>")


def get_html_dom(html_content):
    '''
    Params:
      html_content: the HTML page to retrieve the DOM from.

    Returns:
      The corresponding lxml document object model (DOM).
    '''
    html = RE_FILTER_XML_HEADER.sub("", html_content)
    return etree.HTML(html)


def extract_text(element):
    '''
    Returns:
      str -- The text for the given element.
    '''
    return ' '.join([t.strip() for t in element.itertext() if t.strip()])


def get_xpath_expression(element):
    '''
    Returns:
      str -- The xpath expression for the given comment.
    '''
    xpath_list = []
    has_class_filter = False

    while not has_class_filter and element is not None:
        xpath_expression = _get_xpath_element_expression(element)
        has_class_filter = "[" in xpath_expression
        xpath_list.append(xpath_expression)

        element = element.getparent()

    xpath_list.reverse()
    return "//" + "/".join(xpath_list)


def _get_xpath_element_expression(element):
    '''
    Returns:
      str -- The xpath expression for the given element.
    '''
    attr_filter = " & ".join(['@%s="%s"' % (key, value)
                              for key, value in element.attrib.items()
                              if key in VALID_NODE_TYPE_QUALIFIERS])
    return element.tag + "[%s]" % attr_filter if attr_filter else element.tag


def get_xpath_tree_text(dom, xpath):
    '''
    Args:
      xpath (str): The xpath to extract.
    Returns:
       list -- A list of text obtained by all elements matching the given
       xpath.
    '''
    return [extract_text(element) for element in dom.xpath(xpath)]

def get_cleaned_element_text(element):
    '''
    Returns:
        str -- the text of the given element (without its children and
        punctuation).
    '''
    return f'{element.text or ""} {element.tail or ""}'.replace(",", " ").replace(";", " ").strip()



