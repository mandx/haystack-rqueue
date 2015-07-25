#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(
    name='django-haystack-rqueue',
    version='0.2-alpha',
    description='Delegate object update/deletion to background tasks with RQ (http://python-rq.org)',
    author='Armando Pérez',
    author_email='gmandx@gmail.com',
    url='http://github.com/mandx/haystack-rqueue',
    install_requires=[
        'django-haystack>=2.4',
        'django-rq>=0.5.1',
    ],
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
