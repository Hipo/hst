#!/usr/bin/env python

from setuptools import setup, find_packages

VERSION = '0.1.9'
DESCRIPTION = 'history search & picker in ncurses - also can pick other things'

setup(
    name='hst',
    version=VERSION,
    description=DESCRIPTION,
    author='ybrs',
    license='MIT',
    url="http://github.com/ybrs/hst",
    author_email='aybars.badur@gmail.com',
    packages=['hst'],
    install_requires=['pyperclip'],
    scripts=['./hst/bin/hst'],
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