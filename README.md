# Harvest - A toolkit for extracting posts and post metadata from web forums

[![Actions Status](https://github.com/fhgr/harvest/workflows/build/badge.svg)](https://github.com/fhgr/harvest/actions)
[![codecov](https://codecov.io/gh/fhgr/harvest/branch/main/graph/badge.svg)](
    https://codecov.io/gh/fhgr/harvest)
[![PyPI version](https://badge.fury.io/py/harvest-webforum.svg)](https://badge.fury.io/py/harvest-webforum)

Automatic extraction of forum posts and metadata is a challenging task since forums do not expose their content in a standardized structure. Harvest performs this task reliably for many web forums and offers an easy way to extract data from web forums.

## Installation

At the command line:
```bash
$ pip install harvest-webforum
```

If you want to install from the latest sources, you can do:
```bash
$ git clone https://github.com/fhgr/harvest.git
$ cd harvest
$ python3 setup.py install
```

## Python library
Embedding harvest into your code is easy, as outlined below:
```python
from urllib.request import urlopen, Request
from harvest import extract_data

USER_AGENT = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0"

url = "https://forum.videolan.org/viewtopic.php?f=14&t=145604"
req = Request(url, headers={'User-Agent': USER_AGENT})
html = urlopen(req).read().decode('utf-8')

result = extract_data(html, url)
print(result)
```

## WEB-FORUM-52 gold standard
The [corpus](corpus/goldDocuments) currently contains from 52 different web forums gold standard documents. These documents are also used by the integrations test of harvest.

## Publication

* Weichselbraun, Albert, Brasoveanu, Adrian M. P., Waldvogel, Roger and Odoni, Fabian. (2020). “Harvest - An Open Source Toolkit for Extracting Posts and Post Metadata from Web Forums”. IEEE/WIC/ACM International Joint Conference on Web Intelligence and Intelligent Agent Technology (WI-IAT 2020), Melbourne, Australia, Accepted 27 October 2020.
