#!/usr/bin/env python
# -*- coding: utf-8 -*-
from distutils.core import setup

setup(
    name='haystack-rqueue',
    version='0.1-alpha',
    description='Delegate object update/deletion to background tasks with RQ (http://python-rq.org)',
    author='Armando Pérez',
    author_email='daniel@toastdriven.com',
    url='http://github.com/mandx/haystack-rqueue',
    packages=[
        'haystack_rqueue',
    ],
    classifiers=[
        'Development Status :: 1 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Search',
        'Topic :: Utilities',
    ],
)
