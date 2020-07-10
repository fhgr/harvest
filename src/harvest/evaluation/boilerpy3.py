from boilerpy3 import extractors

from harvest.evaluation.post_splitter import split_into_posts


def get_posts(html, annotations):
    extractor = extractors.DefaultExtractor()
    content = extractor.get_content(html)
    posts = split_into_posts(content, annotations)
    return posts
