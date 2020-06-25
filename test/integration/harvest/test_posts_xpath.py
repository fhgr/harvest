import pytest
import os
import gzip
from json import load
from harvest.posts import extract_posts


@pytest.fixture
def load_test_data():
    def _load_test_data(file_name):
        file_path = os.path.join(os.path.dirname(__file__), '../../../data/forum', file_name)
        with gzip.open(file_path) as f:
            return load(f)

    return _load_test_data


def test_extract_posts_forum_shift_ms(load_test_data):
    forum_test_data = load_test_data("https%3A%2F%2Fshift.ms%2Ftopic%2Fcbd-oil-11.json.gz")
    post = extract_posts(forum_test_data)

    assert post['url'] == 'https://shift.ms/topic/cbd-oil-11'
    assert post['xpath_pattern'] == '//div[@class="bbp-reply-content"]/../..'
    assert post['url_xpath_pattern'] is None
    assert post['date_xpath_pattern'] == '//div/div/div[@class="bbp-reply-date"][not(*) and string-length(text()) > 0]'
    assert post['user_xpath_pattern'] == \
           '//div/div/a[@class="bbp-author-name"][not(*) and string-length(text()) > 0]'


def test_extract_posts_forum_healingwell(load_test_data):
    forum_test_data = load_test_data(
        "https%3A%2F%2Fwww.healingwell.com%2Fcommunity%2Fdefault.aspx%3Ff%3D34%26m%3D4099304.json.gz")
    post = extract_posts(forum_test_data)

    assert post['url'] == 'https://www.healingwell.com/community/default.aspx?f=34&m=4099304'
    assert post['xpath_pattern'] == '//div/div[@class="post-body"]/../../..'
    assert post['url_xpath_pattern'] == \
           '//div[(contains(@class, \'post-even\')) or (contains(@class, \'post-odd\'))]/a[not(*) and string-length(text()) = 0]'
    assert post['date_xpath_pattern'] == '//div/div/div[@class="posted"][not(*) and string-length(text()) > 0]'
    assert post['user_xpath_pattern'] == \
           '//div/div/div/div/div/div/a[@class="user-name"][not(*) and string-length(text()) > 0]'


def test_extract_posts_forum_medhelp(load_test_data):
    forum_test_data = load_test_data("https%3A%2F%2Fwww.medhelp.org%2Fposts%2FHeart-Disease%2FWolfe-Parkinson-"
                                     "White-Syndrome%2Fshow%2F250747.json.gz")
    post = extract_posts(forum_test_data)

    assert post['url'] == 'https://www.medhelp.org/posts/Heart-Disease/Wolfe-Parkinson-White-Syndrome/show/250747'
    assert post['xpath_pattern'] == '//div/div[@class="resp_body "]/..'
    assert post['url_xpath_pattern'] is None
    assert post[
               'date_xpath_pattern'] == '//div/div/div/time[@class="mh_timestamp"][not(*) and string-length(text()) = 0]'
    assert post['user_xpath_pattern'] == '//div/div/div[@class="username"]/a[span]'


def test_extract_posts_forum_medschat(load_test_data):
    forum_test_data = load_test_data("https%3A%2F%2Fwww.medschat.com%2FDiscuss%2Fhow-important-is-this-medician-G-E-"
                                     "Sulfamethoxazole-TMP-DS-Tabitp-to-take-due-to-COPD-206090"
                                     ".htm%3Fsrcq%3Dcopd.json.gz")
    post = extract_posts(forum_test_data)

    assert post['url'] == 'https://www.medschat.com/Discuss/how-important-is-this-medician-G-E-Sulfamethoxazole-' \
                          'TMP-DS-Tabitp-to-take-due-to-COPD-206090.htm?srcq=copd'
    assert post['xpath_pattern'] == '//div/span[@class="search_results"]/../..'
    assert post['url_xpath_pattern'] == '//a[@class="action_bar_blue"][not(*) and string-length(text()) > 0]'
    assert post['date_xpath_pattern'] == '//div/span[@class="small soft"]/time[not(*) and string-length(text()) > 0]'
    assert post[
               'user_xpath_pattern'] == '//div[@class="list_item_b_content"]/strong[not(*) and string-length(text()) > 0]'


def test_extract_posts_forum_msconnection(load_test_data):
    forum_test_data = load_test_data("https%3A%2F%2Fwww.msconnection.org%2FDiscussions%2Ff33%2Ft77364%2Ftp1%2FHow-long-"
                                     "is-too-long-to-wait-for-an-initial-con.json.gz")
    post = extract_posts(forum_test_data)

    assert post['url'] == 'https://www.msconnection.org/Discussions/f33/t77364/tp1/How-long-is-too-long-to-wait-' \
                          'for-an-initial-con'
    assert post['xpath_pattern'] == '//li/div[@class="discussion-post-body"]'
    assert post['url_xpath_pattern'] == None
    assert post['date_xpath_pattern'] == \
           '//header/div/div[@class="discussion-post-meta-info"]/br[not(*) and string-length(text()) = 0]'
    assert post['user_xpath_pattern'] == '//header/div/div/a[@class="PostUser"][not(*) and string-length(text()) > 0]'


def test_extract_posts_forum_msworld(load_test_data):
    forum_test_data = load_test_data("https%3A%2F%2Fwww.msworld.org%2Fforum%2Fshowthread.php%3F145403-"
                                     "Sort-of-new-here.json.gz")
    post = extract_posts(forum_test_data)

    assert post['url'] == 'https://www.msworld.org/forum/showthread.php?145403-Sort-of-new-here'
    assert post['xpath_pattern'] == '//div/blockquote[@class="postcontent restore"]/../../../../..'
    assert post['url_xpath_pattern'] == '//a[@class="postcounter"][not(*) and string-length(text()) > 0]'
    assert post['date_xpath_pattern'] == '//div/div/span/span[@class="date"][span]'
    assert post['user_xpath_pattern'] == \
           '//div/div/div/div/div/a[(contains(@class, \'popupctrl\') and contains(@class, \'username\'))][strong]'


def test_extract_posts_forum_uninterrupted(load_test_data):
    forum_test_data = load_test_data("https%3A%2F%2Fwww.uninterrupted.org.au%2Fblog-category%2Fmy-ms-journey.json.gz")
    post = extract_posts(forum_test_data)

    assert post['url'] == 'https://www.uninterrupted.org.au/blog-category/my-ms-journey'
    assert post['xpath_pattern'] == '//div[@class="field-content"]/../..'
    assert post['url_xpath_pattern'] is None
    assert post['date_xpath_pattern'] is None
    assert post['user_xpath_pattern'] == '//div/span/a[@class="username"][not(*) and string-length(text()) > 0]'

