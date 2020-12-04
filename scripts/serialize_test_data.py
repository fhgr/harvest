#!/usr/bin/env python3

from json import dump

from os.path import exists
from urllib.request import urlopen, Request
from urllib.parse import quote_plus

import datetime
import gzip
import shutil

USER_AGENT = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0"

with open("test-urls.lst") as f:
    for url in (u.strip() for u in f):
        dst = quote_plus(url)
        if exists(dst + ".json") or url.startswith('#') or not url.strip():
            continue

        print("Retrieving", url)
        try:
            req = Request(url, data=None, headers={'User-Agent': USER_AGENT})
            http = urlopen(req)
            content_type = http.getheader('content-type')
            if content_type and 'charset=' in content_type:
                encoding = content_type.split('charset=')[1]
            else:
                encoding = 'utf8'
            html = http.read().decode(encoding)

            with open("../data/" + dst + ".json", 'w') as f:
                dump({'url': url, 'crawled': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'html': html}, f)
            with open("../data/" + dst + ".json", 'rb') as f, \
                    gzip.open('../data/forum/' + dst + ".json.gz", 'wb') as fgzip:
                shutil.copyfileobj(f, fgzip)
        except IOError:
            with open("failed.lst", "a") as f:
                f.write(url + "\n")
