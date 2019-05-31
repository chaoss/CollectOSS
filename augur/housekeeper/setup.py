#!/usr/bin/env python
import os

from setuptools import setup

README = None
with open(os.path.abspath('README.md')) as fh:
    README = fh.read()

setup(
  name='housekeeper',
  version='0.0.1',
  url="https://github.com/chaoss/augur",
  license='MIT',

  author="Augur Team",
  author_email="s@goggins.com",

  description="Augur Worker that collects GitHub data",
  long_description=read("README.rst"),
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
