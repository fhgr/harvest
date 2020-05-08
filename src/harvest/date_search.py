import dateparser.search
import datetime
from harvest.config import LANGUAGES


def search_dates(text):
    results = dateparser.search.search_dates(text, languages=LANGUAGES, settings={'RETURN_AS_TIMEZONE_AWARE': False})
    valid_dates = []
    if results is not None:
        for result in results:
            if result[1] > datetime.datetime(1993, 4, 30):
                valid_dates.append(result)

    return valid_dates
