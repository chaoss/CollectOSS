#!/usr/bin/env python
import os

from setuptools import setup

README = None
with open(os.path.abspath('README.md')) as fh:
    README = fh.read()

setup(
  name='broker_test',
  version='0.0.1',
  description=README,
  author='Carter Landis',
  author_email='ccarterlandis@gmail.com',
  url='https://github.com/ccarterlandis/chambers',
  packages=['broker_test'],
  install_requires=[
    'Flask',
    'sqlalchemy',
    'ipdb',
    'simplejson',
    'pandas',
    'numpy'
  ],
)
