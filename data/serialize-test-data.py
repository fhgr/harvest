#!/usr/bin/env python3

from json import dump

from os.path import exists
from urllib.request import urlopen, Request
from urllib.parse import quote_plus

import gzip


USER_AGENT = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0"

with open("test-urls.lst") as f:
    for url in (u.strip() for u in f):
        dst = quote_plus(url)
        if exists(dst + ".json.gz") or url.startswith('#') or not url.strip():
            continue

        print("Retrieving", url)
        try:
            req = Request(url, data=None,
                          headers={'User-Agent': USER_AGENT})
            http = urlopen(req)
            content_type = http.getheader('content-type')
            if content_type and 'charset=' in content_type:
                encoding = content_type.split('charset=')[1]
            else:
                encoding = 'utf8'
            html = http.read().decode(encoding)
            
            with zip.open(dst + ".json.gz", 'w') as f:
                dump({'url': url, 'html': html}, f)
        except:
            with open("failed.lst", "a") as f:
                f.write(url + "\n")
