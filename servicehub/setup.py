#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function


from setuptools import setup


# @todo import find_packages
def find_packages():
    pass


setup(
    name                = 'servicehub',
    packages            = find_packages(),
    version             = 0.0.1,
    description         = "A single to multi-user service wrapper.",
    author              = "Human Brain Project",
    author_email        = "platform@nbrainproject.eu",
    license             = "BSD",
    platforms           = "Linux",
    python_requires     = ">=3.4",
    classifiers         = [
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
)
