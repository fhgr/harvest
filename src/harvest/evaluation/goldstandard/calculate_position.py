import logging

logging.getLogger().setLevel(logging.INFO)


def _add_start_end(element_to_add, text, sub_text, start_index):
    start_index = text.find(sub_text, start_index)
    if start_index > -1:
        element_to_add['start'] = start_index
        element_to_add['end'] = start_index + len(sub_text)
        return start_index + len(sub_text)
    else:
        logging.warning(f'Not found in text:\n{sub_text}')
        return -1


def get_start_end_for_post(post, full_text, search_start_index):
    index_post_text = [_add_start_end(post['post_text'], full_text, post['post_text']['surface_form'],
                                      search_start_index)]

    if 'datetime' in post:
        index_post_text.append(_add_start_end(post['datetime'], full_text,
                                              post['datetime']['surface_form'], search_start_index))
    if 'user' in post:
        index_post_text.append(_add_start_end(post['user'], full_text,
                                              post['user']['surface_form'], search_start_index))
    if 'post_link' in post:
        index_post_text.append(_add_start_end(post['post_link'], full_text,
                                              post['post_link']['surface_form'], search_start_index))
    return max(index_post_text)
