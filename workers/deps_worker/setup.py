#SPDX-License-Identifier: MIT
import io
import os
import re

from setuptools import find_packages
from setuptools import setup

def read(filename):
    filename = os.path.join(os.path.dirname(__file__), filename)
    text_type = type(u"")
    with io.open(filename, mode="r", encoding='utf-8') as fd:
        return re.sub(text_type(r':[a-z]+:`~?(.*?)`'), text_type(r'``\1``'), fd.read())

setup(
    name="deps_worker",
    version="1.0.0",
    url="https://github.com/chaoss/augur",
    license='MIT',
    author="Stuart Aldrich",
    author_email="stuart.aldrich.1@gmail.com",
    description="Augur Worker that gathers deps data",
    packages=find_packages(exclude=('tests',)),
    install_requires=[
        'Flask==2.0.2',
        'Flask-Cors==3.0.10',
        'Flask-Login==0.5.0',
        'Flask-WTF==1.0.0',
        'requests==2.27.1',
        'psycopg2-binary==2.9.3'
    ],
    entry_points={
        'console_scripts': [
            'deps_worker_start=workers.deps_worker.runtime:main',
        ],
    },

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
    ]
)
