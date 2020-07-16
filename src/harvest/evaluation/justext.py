import justext
import lxml


def _get_language(html):
    lang = "English"
    root = lxml.html.fromstring(html)
    language_construct = root.xpath("//html/@lang")
    if language_construct:
        if 'de' in language_construct[0]:
            lang = "German"
        if 'esn_esp' in language_construct[0]:
            lang = "Spanish"
        if 'fr' in language_construct[0]:
            lang = "French"

    return lang


def get_posts(html):
    html = html.encode('utf-8')
    paragraphs = justext.justext(html, justext.get_stoplist(_get_language(html)))
    # content = [paragraph.text for paragraph in paragraphs if not paragraph.is_boilerplate]
    content = " ".join([paragraph.text for paragraph in paragraphs if not paragraph.is_boilerplate])
    return [content]
