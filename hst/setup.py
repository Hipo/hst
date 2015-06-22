#!/usr/bin/env python

from setuptools import setup, find_packages

VERSION = '0.1'
DESCRIPTION = 'simple object relational mapping (ORM) for mongodb'

setup(
    name='MongoModels',
    version=VERSION,
    description=DESCRIPTION,
    author='ybrs',
    license='MIT',
    url="http://github.com/ybrs/mongomodels",
    author_email='aybars.badur@gmail.com',
    packages=['mongomodels'],
    install_requires=['pymongo', 'inflection'],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Database',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)