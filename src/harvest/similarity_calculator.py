from itertools import chain

from harvest.utils import get_xpath_tree_text
import logging
import re
import numpy as np

VSM_MODEL_SIZE = 5000

# tags that are not allowed to be part of a forum xpath (lowercase)
BLACKLIST_TAGS = ('option', 'footer', 'form', 'head', 'tfoot')
REWARDED_CLASSES = ('content', 'message', 'post', 'wrapper')


def _text_to_vsm(text):
    '''
    translates a text into the vector space model
    using the hashing trick.

    VSM_MODEL_SIZE determines the size of the vsm.
    '''
    vms = np.full(VSM_MODEL_SIZE, 0)
    for word in text.split():
        index = word.__hash__() % VSM_MODEL_SIZE
        vms[index] += 1
    return vms


def _descendants_contain_blacklisted_tag(xpath, dom, blacklisted_tags):
    descendants = set([t.tag for t in chain(*[e.iterdescendants() for e in dom.xpath(xpath)])])
    for tag in blacklisted_tags:
        if tag in descendants:
            return True
    return False


def _ancestors_contains_blacklisted_tag(xpath_string, blacklisted_tags):
    """
    returns
    -------
    True, if the xpath_string (i.e. the ancestors) contains any blacklisted_tag
    """
    xpath = xpath_string.split("/")
    for tag in blacklisted_tags:
        if tag in xpath:
            return True
    return False


def _ancestors_contains_class(xpath, rewarded_classes):
    classes_x_path = re.findall(r"(?!.*\[)@class=\".*\"", xpath)
    if classes_x_path:
        classes = [x.lower() for x in list(filter(None, re.sub(r"@class=|\"", "", classes_x_path[-1]).split(" ")))]
        for html_class in classes:
            for rewarded_class in rewarded_classes:
                if rewarded_class in html_class:
                    return True


def assess_node(reference_content, dom, xpath, reward_classes=False):
    """
    returns
    -------
    a metric that is based on
      (i) the vector space model and
     (ii) the number of returned elements
    (iii) whether the descendants contain any blacklisted tags
    to assess whether the node is likely to be part of a forum post.
    """
    if xpath == "//" or _descendants_contain_blacklisted_tag(xpath, dom, BLACKLIST_TAGS):
        return 0., 1

    xpath_content_list = get_xpath_tree_text(dom, xpath)
    xpath_element_count = len(xpath_content_list)

    reference_vsm = _text_to_vsm(reference_content)
    xpath_vsm = _text_to_vsm(' '.join(xpath_content_list))

    divisor = (np.linalg.norm(reference_vsm) * np.linalg.norm(xpath_vsm))
    if not divisor:
        logging.warning("Cannot compute similarity - empty reference (%s) or xpath (%ss) text.", reference_content,
                        ' '.join(xpath_content_list))
        return 0., 1
    similarity = np.dot(reference_vsm, xpath_vsm) / divisor

    # discount any node that contains BLACKLIST_TAGS
    if _ancestors_contains_blacklisted_tag(xpath, BLACKLIST_TAGS):
        similarity /= 10
    elif reward_classes and _ancestors_contains_class(xpath, REWARDED_CLASSES):
        similarity += 0.1
    return similarity, xpath_element_count
