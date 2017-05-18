#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from setuptools import setup


"""TorIpChanger package installer"""


setup(
    version='0.1.0',
    name='toripchanger',
    url='https://github.com/DusanMadar/TorIpChanger',

    author='Dusan Madar',
    author_email='madar.dusan@gmail.com',

    keywords='change tor ip',
    description='Python powered way to get a unique Tor IP',

    packages=[
        'toripchanger',
        'tests'
    ],

    test_suite='tests',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'Programming Language :: Python :: 3.4',
        'Operating System :: POSIX :: Linux',
        'Natural Language :: English',
    ]
)
