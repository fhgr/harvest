from boilerpy3 import extractors


def get_posts(html):
    extractor = extractors.ArticleExtractor()
    return [extractor.get_content(html)]
