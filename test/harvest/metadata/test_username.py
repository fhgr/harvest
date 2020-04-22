from harvest.metadata.username import get_user_name


def test_get_user_name():
    assert get_user_name('Therese Kurz', 'http://www.heise.de/security') == 'Therese.Kurz@www.heise.de'
