#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# https://github.com/dragnet-org/dragnet
# install: python3 setup.py develop


import sys
from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))
sys.path.insert(0, path.join(here, 'src'))


setup(
    # Metadata
    name="harvest",
    version="0.1",
    description='Forum post harvester.',
    long_description='',
    author='Albert Weichselbraun and Roger Waldvogel',
    author_email='albert.weichselbraun@fhgr.ch, roger.waldvogel@fhgr.ch',
    python_requires='>=3.5',
    license='GPL3',
    package_dir={'': 'src'},

    # Package List
    packages=find_packages('src'),

    # Scripts
    scripts=[
        './src/harvest/main.py'
    ],

    # Requirements
    install_requires=[
        'lxml',
        'requests',
        'dateparser',
        'numpy',
        'inscriptis',
        'flask',
        'fuzzywuzzy'
    ]
)
