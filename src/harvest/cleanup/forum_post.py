#!/usr/bin/env python3

'''
Removes common suffixes and suffixes from forum posts.
'''

import logging

def compute_common_suffix_count(post_list):
    '''
    Returns:
    	int: The number of common suffix terms.
    '''
    confirmed_suffix_terms = []
    for suffix_term in reversed(post_list[0].split(' ')):
        new_suffix = ' ' + ' '.join([suffix_term] + confirmed_suffix_terms)
        for post in post_list:
            if not post.endswith(new_suffix):
                return len(confirmed_suffix_terms)
        confirmed_suffix_terms.insert(0, suffix_term)

    return len(confirmed_suffix_terms)


def remove_suffix(post_list):
    '''
    Removes common suffixes from list posts.
    '''
    suffix_count = compute_common_suffix_count(post_list)
    if suffix_count == 0:
        return post_list
    return [' '.join(posts.split(' ')[:-suffix_count]) for posts in post_list]


def compute_common_prefix_count(post_list):
    '''
    Returns:
    	int: The number of common prefix terms.
    '''
    confirmed_prefix_terms = []
    for prefix_term in post_list[0].split(' '):
        new_prefix = ' '.join(confirmed_prefix_terms + [prefix_term]) + ' '
        for post in post_list:
            if not post.startswith(new_prefix):
                return len(confirmed_prefix_terms)
        confirmed_prefix_terms.append(prefix_term)

    return len(confirmed_prefix_terms)


def remove_prefix(post_list):
    '''
    Removes common suffixes from list posts.
    '''
    prefix_count = compute_common_prefix_count(post_list)
    if prefix_count == 0:
        return post_list
    return [' '.join(posts.split(' ')[prefix_count:]) for posts in post_list]


def remove_boilerplate(post_list):
    '''
    Removes common prefixes and suffixes from list posts.
    '''
    prefix_count = compute_common_prefix_count(post_list)
    suffix_count = compute_common_suffix_count(post_list)
    logging.info(f'{prefix_count}>>{suffix_count}')
    if prefix_count == 0 and suffix_count == 0:
        return post_list
    suffix_count = -suffix_count if suffix_count != 0 else None
    return [' '.join(posts.split(' ')[prefix_count:suffix_count]) for posts in post_list]
