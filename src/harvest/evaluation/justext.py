import justext

from harvest.evaluation.post_splitter import split_into_posts


def get_posts(html, annotations):
    paragraphs = justext.justext(html, justext.get_stoplist("English"))
    content = ''
    for paragraph in paragraphs:
        if not paragraph.is_boilerplate:
            content += paragraph.text
    posts = split_into_posts(content, annotations)
    return posts
