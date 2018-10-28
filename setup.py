#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from setuptools import setup


"""TorIpChanger package installer"""


setup(
    version="1.0.0",
    name="toripchanger",
    url="https://github.com/DusanMadar/TorIpChanger",
    license="MIT",
    author="Dusan Madar",
    author_email="madar.dusan@gmail.com",
    keywords="change tor ip",
    description="Python powered way to get a unique Tor IP",
    packages=["toripchanger", "tests"],
    install_requires=["requests", "stem"],
    test_suite="tests",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
        "Natural Language :: English",
    ],
)
