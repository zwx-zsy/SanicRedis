#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import with_statement
from setuptools import find_packages
import sys
import SanicRedis.BaseRedis as BaseRedis
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
if sys.version_info < (2, 5):
    sys.exit('Python 2.5 or greater is required.')

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

try:
    with open('README.md') as f:
        long_description = f.read()
except Exception as e:
    long_description = None


setup(name='SanicRedis',
      version=BaseRedis.__version__,
      description='SanicRedis',
      long_description=long_description,
      author='zhou biao',
      author_email='vincent321x@gmail.com',
      maintainer='zhou biao',
      maintainer_email='vincent321x@gmail.com',
      url='https://github.com/yancyzhou/SanicRedis',
      packages=find_packages(exclude=["redis", "aioredis"]),
      platforms=['all'],
      classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries'
      ],
      install_requires=['redis','aioredis>=1.1.0']
)