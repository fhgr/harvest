'''
link
----

Tries to obtain the URL of the given post
'''
import logging

from collections import defaultdict
from datetime import datetime
from dateparser.search import search_dates
from dateutil import parser

from harvest.utils import get_xpath_expression, get_cleaned_element_text

MAX_DATE_LEN = 32
LANGUAGES = ('en', 'de', 'es')


# strategy
# --------
# * obtain all xpaths that have date information
#   - extract the one which contains most likely the date (otherwise no date-xpath is returned)

# * extract all dates from the date-xpath
# * select the one that
#   - uses the same format and
#   - are newer (!= join date)

def get_date(dom, post_xpath, base_url, forum_posts):
    '''
    Args:
        dom: The DOM tree to analyze.
        post_xpath (str): xpath of the post to search dates.
        base_url (str): URL of the forum.
    Returns:
        str: the xpath to the post date.
    '''
    date_candidates = defaultdict(lambda: {'elements': [],
                                           'most_recent_date': datetime.fromtimestamp(0),  # 1970
                                           'lowermost_date': datetime.fromtimestamp(1E11),  # >5000
                                           'chronological_order': True,
                                           'same_size_posts': False,
                                           'multiple_dates': False})

    # post elements contains less elements than forum_posts (!)
    # since it takes the container with the posts
    post_elements = dom.xpath(post_xpath + "/..")

    # collect candidate paths
    for element in post_elements:
        for tag in element.iterdescendants():
            text = get_cleaned_element_text(tag)
            # do not consider text larger than MAX_DATE_LEN relevant for date extraction

            if len(text) > MAX_DATE_LEN or not search_dates(text, languages=LANGUAGES) and not (
                    tag.tag == 'time' and 'datetime' in tag.attrib):
                continue

            xpath = post_xpath + get_xpath_expression(tag)
            date_candidates[xpath]['elements'].append(tag)

    # filter candidate paths that do not yield a date for every post
    for xpath, matches in list(date_candidates.items()):
        # consider the number of posts or the number of posts + 2 spare for possible header elements
        if len(forum_posts) - len(matches['elements']) not in range(0, 3):
            del date_candidates[xpath]

    # Set if same length as posts
    for xpath, matches in list(date_candidates.items()):
        if len(forum_posts) == len(matches['elements']):
            matches['same_size_posts'] = True

    # rank candidates based on the following criteria
    # - they must yield a date for every post
    # - we choose the candidate with the most recent date
    #   (to distinguish between "post" and "member since" dates minus 1 year per year timedelta between the dates)
    for xpath, matches in list(date_candidates.items()):
        previous_date = datetime.min
        for match in matches['elements']:
            logging.info("Match attribs: %s of type %s.", match, type(match))

            if match.tag == 'time':
                time = match.attrib.get('datetime', '')
                extracted_dates = [(time, parser.parse(time, ignoretz=True))]
            else:
                extracted_dates = search_dates(get_cleaned_element_text(match), languages=LANGUAGES)

            if not extracted_dates:
                del date_candidates[xpath]
                break

            if len(extracted_dates) > 1:
                date_candidates[xpath]['multiple_dates'] = True
                date_candidates[xpath]['most_recent_date'] = max(date_candidates[xpath]['most_recent_date'],
                                                                 max([date[1] for date in extracted_dates]))
                date_candidates[xpath]['lowermost_date'] = min(date_candidates[xpath]['lowermost_date'],
                                                               min([date[1] for date in extracted_dates]))

                if previous_date > max([date[1] for date in extracted_dates]):
                    date_candidates[xpath]['chronological_order'] = False
            else:
                date_candidates[xpath]['most_recent_date'] = max(date_candidates[xpath]['most_recent_date'],
                                                                 extracted_dates[0][1])
                date_candidates[xpath]['lowermost_date'] = min(date_candidates[xpath]['lowermost_date'],
                                                               extracted_dates[0][1])
                if previous_date > extracted_dates[0][1]:
                    date_candidates[xpath]['chronological_order'] = False

            previous_date = date_candidates[xpath]['most_recent_date']


    # obtain the most likely url path
    if len(date_candidates) > 1:
        logging.info("%d rather than one URL candidate remaining. "
                     "Sorting candidates.", len(date_candidates))
    for xpath, _ in sorted(date_candidates.items(),
                           key=lambda x: (x[1]['same_size_posts'], x[1]['chronological_order'],
                                          x[1]['most_recent_date'] - x[1]['lowermost_date']),
                           reverse=True):
        logging.info("Computed URL xpath for forum %s.", base_url)
        return xpath

    return None
