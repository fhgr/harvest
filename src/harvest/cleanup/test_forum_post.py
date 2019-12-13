#!/usr/bin/env python3

'''
Test classes
'''

from harvest.cleanup.forum_post import remove_suffix, remove_prefix, remove_boilerplate

def test_remove_suffix():
    post_list = ['Good day', 'Good Saturday', 'Good Wednesday']
    assert remove_suffix(post_list) == post_list

    post_list2 = ['Good day [Reply - to]', 'Good Saturday [Reply - to]', 'Good Wednesday [Reply - to]']
    assert remove_suffix(post_list2) == post_list

    assert remove_prefix(post_list) == ['day', 'Saturday', 'Wednesday']


#
# tests based on reported errors
#

def test_missing_message():
    '''
    the following string got completely removed by cleaning.
    '''
    s = ["Add message | Report paperplant Thu 21-Nov-19 11:07:27 Following as non-white woman - sounds really interesting, thanks for posting. Can't say much as I've only experienced the booking/sickle cell test and in my hospital we're offered the BCG vaccine as routine. My area is about 50% South Asian ethnicity though.", 
          "Add message | Report Lweji Thu 21-Nov-19 11:27:03 Is that actually true? Anatomy, etc? Have you found evidence other than being told about it by a midwife?"]

    assert remove_boilerplate(s) == ["paperplant Thu 21-Nov-19 11:07:27 Following as non-white woman - sounds really interesting, thanks for posting. Can't say much as I've only experienced the booking/sickle cell test and in my hospital we're offered the BCG vaccine as routine. My area is about 50% South Asian ethnicity though.",
                                     "Lweji Thu 21-Nov-19 11:27:03 Is that actually true? Anatomy, etc? Have you found evidence other than being told about it by a midwife?"]

