#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import with_statement

import sys
if sys.version_info < (2, 5):
    sys.exit('Python 2.5 or greater is required.')

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import BaseRedis


with open('README.rst') as fp:
    readme = fp.read()

with open('LICENSE') as fp:
    license = fp.read()

setup(name='sanic_redis',
      version=BaseRedis.__version__,
      description='Simple xml parse and build lib.',
      long_description=readme,
      author='zhou biao',
      author_email='vincent321x@gmail.com',
      maintainer='zhou biao',
      maintainer_email='vincent321x@gmail.com',
      url='https://github.com/heronotears/lazyxml',
      packages=['sanic_redis'],
      license=license,
      platforms=['any'],
      classifiers=[])