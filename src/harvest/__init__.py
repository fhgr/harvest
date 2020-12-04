"""
Automatic extraction of forum posts and metadata is a challenging task since forums do not expose their content in a
standardized structure. Harvest performs this task reliably for many web forums and offers an easy way to extract data
from web forums.
Example::
   import urllib.request
   from inscriptis import get_text
   url = 'https://www.fhgr.ch'
   html = urllib.request.urlopen(url).read().decode('utf-8')
   text = get_text(html)
   print(text)
"""

__author__ = 'Albert Weichselbraun, Roger Waldvogel'
__author_email__ = 'albert.weichselbraun@fhgr.ch, roger.waldvogel@fhgr.ch'
__copyright__ = '2019-2020 Albert Weichselbraun, Roger Waldvogel'
__license__ = 'Apache-2.0'
__version__ = '1.0.0'
__status__ = 'Prototype'

try:
    import re
    from lxml.html import fromstring

    from harvest import posts
    from harvest.extract import extract_posts

except ImportError:
    import warnings

    warnings.warn(
        "Missing dependencies - harvest has not been properly installed")

RE_STRIP_XML_DECLARATION = re.compile(r'^<\?xml [^>]+?\?>')


def extract_data(html, url):
    """

    Args:

    Returns:

    """
    extract_post_result = posts.extract_posts(html, url)
    extraction_results = extract_posts(html, url, extract_post_result['text_xpath_pattern'],
                                       extract_post_result['url_xpath_pattern'],
                                       extract_post_result['date_xpath_pattern'],
                                       extract_post_result['user_xpath_pattern'])

    final_results = []
    for extraction_result in extraction_results:
        entity = {'post': extraction_result.post}
        if hasattr(extraction_result, 'date'):
            entity['date'] = extraction_result.date
        if hasattr(extraction_result, 'url'):
            entity['url'] = extraction_result.url
        if hasattr(extraction_result, 'user'):
            entity['user'] = extraction_result.user
        final_results.append(entity)

    return {posts: final_results}
