from harvest.utils import get_merged_xpath


def test_get_merge_xpath():
    xpaths = [r'//div[@class="post post-even"]/a[not(*) and string-length(text()) = 0]',
              r'//div[@class="post-odd"]/a[not(*) and string-length(text()) = 0]',
              r'//a[@class="user-name"][not(*) and string-length(text()) > 0]']
    merged_xpath = get_merged_xpath(xpaths)
    assert len(merged_xpath) == 1
    assert merged_xpath[0] == r"//div[(contains(@class, 'post') and contains(@class, 'post-even')) or " \
                              r"(contains(@class, 'post-odd'))]" \
                              r"/a[not(*) and string-length(text()) = 0]"


def test_get_merge_xpath_same_classes():
    xpaths = [r'//div[@class="post post-even"]/a[not(*) and string-length(text()) = 0]',
              r'//div[@class="post post-odd"]/a[not(*) and string-length(text()) = 0]',
              r'//a[@class="user-name"][not(*) and string-length(text()) > 0]']
    merged_xpath = get_merged_xpath(xpaths)
    assert len(merged_xpath) == 1
    assert merged_xpath[0] == r"//div[(contains(@class, 'post'))]" \
                              r"/a[not(*) and string-length(text()) = 0]"


def test_get_merge_xpath_with_no_merges():
    xpaths = [r'//div[@class="post post-odd"]/a[not(*) and string-length(text()) = 0]',
              r'//a[@class="user-name"][not(*) and string-length(text()) > 0]']
    merged_xpath = get_merged_xpath(xpaths)
    assert not merged_xpath
