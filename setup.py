#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import with_statement
from setuptools import find_packages
import ssl
ssl._create_default_https_context=ssl._create_unverified_context
import sys
if sys.version_info < (2, 5):
    sys.exit('Python 2.5 or greater is required.')

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
import SanicRedis.BaseRedis as BaseRedis


setup(name='SanicRedis',
      version=BaseRedis.__version__,
      description='Simple xml parse and build lib.',
      long_description="SanicRedis is a sanic framework extension which adds support for the redis.",
      author='zhou biao',
      author_email='vincent321x@gmail.com',
      maintainer='zhou biao',
      maintainer_email='vincent321x@gmail.com',
      url='https://github.com/yancyzhou/sanic_redis',
      install_requires=['redis'],
      packages=find_packages(),
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
      ])