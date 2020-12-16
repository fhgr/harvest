import logging
import re
from fuzzywuzzy import fuzz

logging.getLogger().setLevel(logging.INFO)


def _add_start_end_fuzzy_search(element_to_add, text, sub_text, start_index, move_text_left=0):
    sub_text_start = re.sub(r'(?<!AM|PM)( \.)', '.', sub_text[move_text_left:30 + move_text_left])
    sub_text_end = re.sub(r'(?<!AM|PM)( \.)', '.', sub_text[-30:])
    sub_text_start_index = text.find(sub_text_start, start_index)
    if sub_text_start_index > -1:
        sub_text_end_index = text.find(sub_text_end, sub_text_start_index)
        if sub_text_end_index > -1:
            sub_text_end_index = sub_text_end_index + len(sub_text_end)
            matched_text = text[sub_text_start_index:sub_text_end_index]
            if fuzz.ratio(matched_text, sub_text) > 70:
                element_to_add['start'] = sub_text_start_index
                element_to_add['end'] = sub_text_end_index
                return element_to_add['end']
    elif move_text_left < len(sub_text) - 60:
        return _add_start_end_fuzzy_search(element_to_add, text, sub_text, start_index, move_text_left + 20)
    logging.warning(f'Not found in text:\n{sub_text}')
    return -1


def _add_start_end(element_to_add, text, sub_text, start_index, fuzzy_search=False):
    if isinstance(sub_text, str):
        found_start_index = text.find(sub_text, start_index)
        if found_start_index > -1:
            element_to_add['start'] = found_start_index
            element_to_add['end'] = found_start_index + len(sub_text)
            return found_start_index + len(sub_text)
        elif fuzzy_search and len(sub_text) > 150:
            return _add_start_end_fuzzy_search(element_to_add, text, sub_text, start_index)
        else:
            logging.warning(f'Not found in text:\n{sub_text}')
            return -1
    return -1


def get_start_end_for_post(post, full_text, search_start_index, fuzzy_search=False):
    index_post_text = _add_start_end(post['post_text'], full_text, post['post_text']['surface_form'],
                                     search_start_index, fuzzy_search)

    if 'datetime' in post:
        _add_start_end(post['datetime'], full_text,
                       post['datetime']['surface_form'], search_start_index)
    if 'user' in post:
        _add_start_end(post['user'], full_text,
                       post['user']['surface_form'], search_start_index)
    if 'post_link' in post:
        _add_start_end(post['post_link'], full_text,
                       post['post_link']['surface_form'], search_start_index)
    if index_post_text > -1:
        return index_post_text + len(post['post_text'])
    return index_post_text
