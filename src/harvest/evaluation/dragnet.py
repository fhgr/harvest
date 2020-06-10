from dragnet import extract_content_and_comments
from harvest.date_search import search_dates


def date_in_header(text):
    return search_dates(text) and len(text) < 120


def get_posts(html):
    content_comments = extract_content_and_comments(html, encoding=None, as_blocks=True)

    return [c.text.decode("utf-8") for c in content_comments
            if not date_in_header(c.text.decode("utf-8"))]
