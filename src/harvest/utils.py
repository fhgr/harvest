'''
Functions that are shared across modules.
'''

import re

from lxml import etree

VALID_NODE_TYPE_QUALIFIERS = ('class',)
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


def get_xpath_expression_child_filter(element):
    """
    Returns:
        str -- The xpath expression to filter because of child element
    """
    child_filter = ""
    children = element.getchildren()
    if len(children) == 1 and type(children[0].tag) == str:
        child_filter = "[" + children[0].tag + "]"
    elif element.text and element.text.strip() and not children:
        child_filter = "[not(*) and string-length(text()) > 0]"
    elif not element.text and not children:
        child_filter = "[not(*) and string-length(text()) = 0]"
    return child_filter


def get_xpath_combinations_for_classes(x_path):
    """
    Returns:
        array -- Possible xpath combinations of classes
    """
    classes_x_path = re.findall(r"(?!.*\[)@class=\".*\"", x_path)
    xpath_combinations = []
    if classes_x_path:
        classes = list(filter(None, re.sub(r"@class=|\"", "", classes_x_path[-1]).split(" ")))
        for html_class in classes:
            xpath_combinations.append(
                re.sub(r"(?!.*\[)@class=\".*\"\]", r"contains(concat(' ',@class,' '),' " + html_class + r" ')]",
                       x_path))
        if len(classes) > 1:
            new_classes = " and ".join(["contains(@class, \'" + x + "\')" for x in classes]) + "]"
            xpath_combinations.append(re.sub(r"(?!.*\[)@class=\".*\"\]", new_classes, x_path))
    if not xpath_combinations:
        xpath_combinations = [x_path]
    return xpath_combinations


def get_xpath_expression(element, parent_element=None, single_class_filter=False):
    '''
    Returns:
      str -- The xpath expression for the given comment.
    '''
    xpath_list = []
    has_class_filter = False

    while (not has_class_filter or parent_element is not None and element is not parent_element) \
            and element is not None:
        without_class_filter = single_class_filter and has_class_filter
        xpath_expression = _get_xpath_element_expression(element, without_class_filter=without_class_filter)
        if not has_class_filter and "[" in xpath_expression:
            has_class_filter = True
        # Todo does this improve the detection overall?
        # if not has_class_filter:
        #    xpath_expression = xpath_expression + "[not(@class)]"
        xpath_list.append(xpath_expression)

        element = element.getparent()

    xpath_list.reverse()
    return "//" + "/".join(xpath_list)


def _get_xpath_element_expression(element, without_class_filter=False):
    '''
    Returns:
      str -- The xpath expression for the given element.
    '''
    attr_filter = None
    if not without_class_filter:
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
    return [re.sub(r'\s\s+', ' ', extract_text(element)) for element in dom.xpath(xpath)]


def get_cleaned_element_text(element):
    '''
    Returns:
        str -- the text of the given element (without its children and
        punctuation).
    '''
    return f'{element.text or ""} {element.tail or ""}'.replace(",", " ") \
        .replace(";", " ").strip()


def _get_classes_concat_with_and_condition(classes):
    return "(" + " and ".join(["contains(@class, \'" + x + "\')" for x in classes]) + ")"


def _get_merged_classes_xpath_condition(classes, classes2):
    return "[" + _get_classes_concat_with_and_condition(classes) + " or " + \
           _get_classes_concat_with_and_condition(classes2) + "]"


def _get_classes(regex_class_detection, xpath):
    """
    Args:
        regex_class_detection: regex to detect class
        xpath: xpath string to get classes

    Returns: list of classes
    """
    classes = re.findall(regex_class_detection, xpath)
    return list(filter(None, re.sub(r"@class=|\"|\[|\]", "", classes[0]).split(" ")))


def _get_merged_xpath(regex_class_detection, xpath, xpath_to_compare, merged_xpath):
    """
    Args:
        regex_class_detection: Regex expression to look for class attributes
        xpath: xpath string
        xpath_to_compare: xpath string to compare with param xpath
        merged_xpath: dictionary with already merged xpath

    Returns: merged xpath if possible. If no match is found, none is returned

    """
    xpath_without_class = re.sub(regex_class_detection, "", xpath)
    xpath_to_compare_without_class = re.sub(regex_class_detection, "", xpath_to_compare)
    if xpath_without_class == xpath_to_compare_without_class and xpath_to_compare not in merged_xpath:
        classes = _get_classes(regex_class_detection, xpath)
        classes_to_compare = _get_classes(regex_class_detection, xpath_to_compare)
        same_classes = list(set(classes).intersection(classes_to_compare))
        if same_classes:
            same_classes.sort()
            return re.sub(regex_class_detection, "[" + _get_classes_concat_with_and_condition(same_classes) + "]",
                          xpath)

        if classes and classes_to_compare:
            merged_xpath_classes = _get_merged_classes_xpath_condition(classes, classes_to_compare)
            return re.sub(regex_class_detection, merged_xpath_classes, xpath)


def get_merged_xpath(xpaths):
    """
    Args:
        xpaths: List of xpaths to look for xpaths which can be merged

    Returns: A list with the merged xpath
    """
    merged_xpaths = dict()
    regex_class_detection = r"\[@class=\".*\"\]"
    for xpath in xpaths:
        if re.search(regex_class_detection, xpath):
            for xpath_to_compare in [x for x in xpaths if x != xpath]:
                if re.search(regex_class_detection, xpath_to_compare):
                    merged_xpath = _get_merged_xpath(regex_class_detection, xpath, xpath_to_compare, merged_xpaths)
                    if merged_xpath:
                        merged_xpaths[xpath] = merged_xpath

    return list(merged_xpaths.values())


def get_grandparent(element):
    if etree.iselement(element) and etree.iselement(element.getparent()) and \
            etree.iselement(element.getparent().getparent()):
        return element.getparent().getparent()


def elements_have_no_overlap(elements):
    for element in elements:
        for element_to_compare in [child for child in [x for x in elements if x is not element]]:
            for child_element in element.iterdescendants():
                if element_to_compare is child_element:
                    return False
    return True
