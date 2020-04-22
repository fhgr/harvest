import pytest
import os
import gzip
from json import load
from harvest.posts import extract_posts


@pytest.fixture
def load_test_data():
    def _load_test_data(file_name):
        file_path = os.path.join(os.path.dirname(__file__), '../../data/forum', file_name)
        with gzip.open(file_path) as f:
            return load(f)

    return _load_test_data


def test_extract_posts_forum_angelman(load_test_data):
    forum_test_data = load_test_data("http%3A%2F%2Fblog.angelman-asa.org%2Fread.php%3F2%2C736.json.gz")
    post = extract_posts(forum_test_data)

    assert post['url'] == 'http://blog.angelman-asa.org/read.php?2,736'
    assert post['xpath_pattern'] == '//div[@class="message-body"]/..'
    assert post['url_xpath_pattern'] == '//html/body/div/a[not(*) and string-length(text()) = 0]'
    assert post['date_xpath_pattern'] == \
           '//div[@class="generic"]/table/tr/td/small/br[not(*) and string-length(text()) = 0]'
    assert post['user_xpath_pattern'] == \
           '//div[@class="message-author icon-user"]/a[not(*) and string-length(text()) > 0]'


def test_extract_posts_forum_community_scope(load_test_data):
    forum_test_data = load_test_data("https%3A%2F%2Fcommunity.scope.org.uk%2Fdiscussion%2F57774%2Fcopd.json.gz")
    post = extract_posts(forum_test_data)

    assert post['url'] == 'https://community.scope.org.uk/discussion/57774/copd'
    assert post['xpath_pattern'] == \
           '//div[contains(@class, \'Message\') and contains(@class, \'userContent\')]/../../../..'
    assert post['url_xpath_pattern'] is None
    assert post['date_xpath_pattern'] == \
           '//a[@class="Permalink"]/time[not(*) and string-length(text()) > 0]'
    assert post['user_xpath_pattern'] == \
           '//a[@class="Username"][not(*) and string-length(text()) > 0]'


def test_extract_posts_forum_maladiesraresinfo(load_test_data):
    forum_test_data = load_test_data("https%3A%2F%2Fforums.maladiesraresinfo.org%2Fpost11011.html%23p11011.json.gz")
    post = extract_posts(forum_test_data)

    assert post['url'] == 'https://forums.maladiesraresinfo.org/post11011.html#p11011'
    assert post['xpath_pattern'] == '//div[@class="content"]/../..'
    assert post['url_xpath_pattern'] == '//a[@class="top"][not(*) and string-length(text()) > 0]'
    assert post['date_xpath_pattern'] == '//p[@class="author"]/strong[a]'
    assert post['user_xpath_pattern'] == \
           '//dl[@class="postprofile"]/dt/a[not(*) and string-length(text()) > 0]'


def test_extract_posts_forum_healthunlocked(load_test_data):
    forum_test_data = load_test_data(
        "https%3A%2F%2Fhealthunlocked.com%2Fparkinsonsmovement%2Fposts%2F142058845%2Fartane-anyone.json.gz")
    post = extract_posts(forum_test_data)

    assert post['url'] == 'https://healthunlocked.com/parkinsonsmovement/posts/142058845/artane-anyone'
    assert post['xpath_pattern'] == \
           '//div[contains(@class, \'response-text-content\') and contains(@class, \'text-content\')]/span/p/../../..'
    assert post['url_xpath_pattern'] == \
           '//div[@class="post-media-info__action"]/a[not(*) and string-length(text()) > 0]'
    assert post['date_xpath_pattern'] == '//time[@class=""][not(*) and string-length(text()) > 0]'
    assert post['user_xpath_pattern'] == \
           '//div[@class="response-header__author-content"]/a[not(*) and string-length(text()) > 0]'


def test_extract_posts_forum_myparkinsons(load_test_data):
    forum_test_data = load_test_data(
        "https%3A%2F%2Fmyparkinsons.org%2Fcgi-bin%2Fforum%2Ftopic_show.pl%3Fid%3D5231.json.gz")
    post = extract_posts(forum_test_data)

    assert post['url'] == 'https://myparkinsons.org/cgi-bin/forum/topic_show.pl?id=5231'
    assert post['xpath_pattern'] == '//html/body/div/center/table/center/table/tr/td/../..'
    assert post['url_xpath_pattern'] is None
    assert post['date_xpath_pattern'] == \
           '//html/body/div/center/table/center/table/tr/td/table/tr/td/b[not(*) and string-length(text()) > 0]'
    assert post['user_xpath_pattern'] == \
           '//html/body/div/center/table/center/table/tr/td/table/tr/td/a[not(*) and string-length(text()) > 0]'


def test_extract_posts_forum_shift_ms(load_test_data):
    forum_test_data = load_test_data("https%3A%2F%2Fshift.ms%2Ftopic%2Fcbd-oil-11.json.gz")
    post = extract_posts(forum_test_data)

    assert post['url'] == 'https://shift.ms/topic/cbd-oil-11'
    assert post['xpath_pattern'] == '//div[@class="bbp-reply-content"]/p/../../..'
    assert post['url_xpath_pattern'] is None
    assert post['date_xpath_pattern'] == '//div[@class="bbp-reply-date"][not(*) and string-length(text()) > 0]'
    assert post['user_xpath_pattern'] == \
           '//a[@class="bbp-author-name"][not(*) and string-length(text()) > 0]'


def test_extract_posts_forum_amsel(load_test_data):
    forum_test_data = load_test_data("https%3A%2F%2Fwww.amsel.de%2Fmultiple-sklerose-forum%2F%3Ftnr%3D1%26mnr%3D217239"
                                     "%26archiv_flag%3D2%26fv%3D1.json.gz")
    post = extract_posts(forum_test_data)

    assert post['url'] == 'https://www.amsel.de/multiple-sklerose-forum/?tnr=1&mnr=217239&archiv_flag=2&fv=1'
    assert post['xpath_pattern'] == '//td[contains(@class, \'forum_message\') and contains(@class, \'bg_7\')]/..'
    assert post['url_xpath_pattern'] == '//td[@class="bg_7 x_textsize_1"]/p/a[not(*) and string-length(text()) = 0]'
    assert post['date_xpath_pattern'] == \
           '//td[@class="bg_3 x_textsize_1"]/p[not(*) and string-length(text()) > 0]'
    assert post['user_xpath_pattern'] == \
           '//td[@class="bg_7 x_textsize_1"]/p/a[not(*) and string-length(text()) > 0]'


def test_extract_posts_forum_healingwell(load_test_data):
    forum_test_data = load_test_data(
        "https%3A%2F%2Fwww.healingwell.com%2Fcommunity%2Fdefault.aspx%3Ff%3D34%26m%3D4099304.json.gz")
    post = extract_posts(forum_test_data)

    assert post['url'] == 'https://www.healingwell.com/community/default.aspx?f=34&m=4099304'
    assert post['xpath_pattern'] == '//div[@class="post-body"]/../../..'
    assert post['url_xpath_pattern'] == \
           '//div[(contains(@class, \'post-even\')) or (contains(@class, \'post-odd\'))]/a[not(*) and string-length(text()) = 0]'
    assert post['date_xpath_pattern'] == '//div[@class="posted"][not(*) and string-length(text()) > 0]'
    assert post['user_xpath_pattern'] == \
           '//a[@class="user-name"][not(*) and string-length(text()) > 0]'


def test_extract_posts_forum_medhelp(load_test_data):
    forum_test_data = load_test_data("https%3A%2F%2Fwww.medhelp.org%2Fposts%2FHeart-Disease%2FWolfe-Parkinson-"
                                     "White-Syndrome%2Fshow%2F250747.json.gz")
    post = extract_posts(forum_test_data)

    assert post['url'] == 'https://www.medhelp.org/posts/Heart-Disease/Wolfe-Parkinson-White-Syndrome/show/250747'
    assert post['xpath_pattern'] == '//div[@class="resp_body "]/..'
    assert post['url_xpath_pattern'] is None
    assert post['date_xpath_pattern'] == '//time[@class="mh_timestamp"][not(*) and string-length(text()) = 0]'
    assert post['user_xpath_pattern'] == '//div[@class="username"]/a[span]'


def test_extract_posts_forum_medschat(load_test_data):
    forum_test_data = load_test_data("https%3A%2F%2Fwww.medschat.com%2FDiscuss%2Fhow-important-is-this-medician-G-E-"
                                     "Sulfamethoxazole-TMP-DS-Tabitp-to-take-due-to-COPD-206090"
                                     ".htm%3Fsrcq%3Dcopd.json.gz")
    post = extract_posts(forum_test_data)

    assert post['url'] == 'https://www.medschat.com/Discuss/how-important-is-this-medician-G-E-Sulfamethoxazole-' \
                          'TMP-DS-Tabitp-to-take-due-to-COPD-206090.htm?srcq=copd'
    assert post['xpath_pattern'] == '//span[@class="search_results"]/../..'
    assert post['url_xpath_pattern'] == '//a[@class="action_bar_blue"][not(*) and string-length(text()) > 0]'
    assert post['date_xpath_pattern'] == '//span[@class="small soft"]/time[not(*) and string-length(text()) > 0]'
    assert post['user_xpath_pattern'] is None # Todo extract user with no link


def test_extract_posts_forum_msconnection(load_test_data):
    forum_test_data = load_test_data("https%3A%2F%2Fwww.msconnection.org%2FDiscussions%2Ff33%2Ft77364%2Ftp1%2FHow-long-"
                                     "is-too-long-to-wait-for-an-initial-con.json.gz")
    post = extract_posts(forum_test_data)

    assert post['url'] == 'https://www.msconnection.org/Discussions/f33/t77364/tp1/How-long-is-too-long-to-wait-' \
                          'for-an-initial-con'
    assert post['xpath_pattern'] == '//div[@class="discussion-post-body"]'
    assert post['url_xpath_pattern'] == None
    assert post['date_xpath_pattern'] == \
           '//div[@class="discussion-post-meta-info"]/br[not(*) and string-length(text()) = 0]'
    assert post['user_xpath_pattern'] == '//a[@class="PostUser"][not(*) and string-length(text()) > 0]'


def test_extract_posts_forum_msworld(load_test_data):
    forum_test_data = load_test_data("https%3A%2F%2Fwww.msworld.org%2Fforum%2Fshowthread.php%3F145403-"
                                     "Sort-of-new-here.json.gz")
    post = extract_posts(forum_test_data)

    assert post['url'] == 'https://www.msworld.org/forum/showthread.php?145403-Sort-of-new-here'
    assert post['xpath_pattern'] == \
           '//blockquote[contains(@class, \'postcontent\') and contains(@class, \'restore\')]/../../../../..'
    assert post['url_xpath_pattern'] == '//a[@class="postcounter"][not(*) and string-length(text()) > 0]'
    assert post['date_xpath_pattern'] == '//span[@class="date"][span]'
    assert post['user_xpath_pattern'] == \
           '//a[(contains(@class, \'popupctrl\') and contains(@class, \'username\'))][strong]'


def test_extract_posts_forum_mumsnet(load_test_data):
    forum_test_data = load_test_data("https%3A%2F%2Fwww.mumsnet.com%2FTalk%2Fpregnancy%2F3749275-Pregnant-with-a-black"
                                     "-mixed-race-with-black-baby.json.gz")
    post = extract_posts(forum_test_data)

    assert post['url'] == \
           'https://www.mumsnet.com/Talk/pregnancy/3749275-Pregnant-with-a-black-mixed-race-with-black-baby'
    assert post['xpath_pattern'] == \
           '//div[contains(@class, \'talk-post\') and contains(@class, \'message\')]/p/../..'
    assert post['url_xpath_pattern'] is None
    assert post['date_xpath_pattern'] == \
           '//span[@class="post_time"][not(*) and string-length(text()) > 0]'
    assert post['user_xpath_pattern'] == None # Todo extract user with no link


def test_extract_posts_forum_uninterrupted(load_test_data):
    forum_test_data = load_test_data("https%3A%2F%2Fwww.uninterrupted.org.au%2Fblog-category%2Fmy-ms-journey.json.gz")
    post = extract_posts(forum_test_data)

    assert post['url'] == 'https://www.uninterrupted.org.au/blog-category/my-ms-journey'
    assert post['xpath_pattern'] == '//div[@class="field-content"]/p/../../..'
    assert post['url_xpath_pattern'] is None
    assert post['date_xpath_pattern'] is None
    assert post['user_xpath_pattern'] == '//a[@class="username"][not(*) and string-length(text()) > 0]'
