from harvest.date_search import search_dates
import datetime


def test_date_found_by_external_library():
    result = search_dates("asdfad 25-February-2012 21:46  afd adsf")
    assert len(result) == 1
    assert result[0][0] == "25-February-2012 21:46"
    assert result[0][1] == datetime.datetime(2012, 2, 25, 21, 46)


def test_date_found_by_external_library_is_to_old():
    result = search_dates("asdfad 29-April-1993 21:46  afd adsf")
    assert len(result) == 0
