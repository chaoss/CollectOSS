#!/usr/bin/env python
import os

from setuptools import setup

README = None
with open(os.path.abspath('README.md')) as fh:
    README = fh.read()

setup(
  name='housekeeper_test',
  version='0.0.1',
  description=README,
  author='Gabe Heim',
  author_email='gabe@gabehe.im',
  url='https://github.com/chaoss/augur',
  packages=['housekeeper_test'],
  install_requires=[
    'Flask',
    'sqlalchemy',
    'ipdb',
    'simplejson',
    'pandas',
    'numpy'
  ],
)
