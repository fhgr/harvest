'''
Functions that are shared across modules.
'''

VALID_NODE_TYPE_QUALIFIERS = ('class', )

def extract_text(element):
    ''' 
    returns
    -------
    the text for the given element 
    '''
    return ' '.join([t.strip() for t in element.itertext() if t.strip()])


def get_xpath_expression(element):
    '''
    returns
    -------
    the xpath expression for the given comment.
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
    returns
    -------
    the xpath expression for the given element
    '''
    attr_filter = " & ".join(['@%s="%s"' % (key, value)
                              for key, value in element.attrib.items()
                              if key in VALID_NODE_TYPE_QUALIFIERS])
    return element.tag + "[%s]" % attr_filter if attr_filter else element.tag
