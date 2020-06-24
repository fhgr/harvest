from inscriptis import get_text

WORDS_TO_IGNORE_DE = {'cookies', 'startseite', 'datenschutzerklärung', 'impressum', 'nutzungsbedingungen',
                      'registrieren'}
WORDS_TO_IGNORE_EN = {'forum home', 'sign in', 'sign up'}
WORDS_TO_IGNORE = WORDS_TO_IGNORE_DE.union(WORDS_TO_IGNORE_EN)


def get_cleaned_text(html):
    text_sections = []
    text = get_text(html)
    for comment in (c for c in text.split("\n") if c.strip()):
        if [word for word in WORDS_TO_IGNORE if word in comment.lower()]:
            continue
        elif 'copyright' not in comment.lower() and '©' not in comment.lower() and 'powered by' not in comment.lower():
            text_sections.append(comment.strip())
        else:
            break
    return text_sections