#!/usr/bin/env python

import os
from io import open
from setuptools import setup, find_packages
import pcsnap

fpk=find_packages(where=".")
print(fpk)

setup(
    name='pcsnap',
    version=pcsnap.__version__,
    description=pcsnap.__description__,
    author=pcsnap.__author__,
    packages=fpk,

    zip_safe=False,

    keywords=pcsnap.__keywords__,
    python_requires='>=3.6',
    setup_requires=[],

    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    entry_points={
        'console_scripts': [
            'pcsnap=pcsnap.__main__:main',
            'gitwalker=pcsnap.gitwalker2:main'
        ]
    }
)
