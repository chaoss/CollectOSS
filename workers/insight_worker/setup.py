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
    name="insight_worker",
    version="1.0.0",
    url="https://github.com/chaoss/augur",
    license='MIT',
    author="Augurlabs",
    author_email="s@goggins.com",
    description="Augur Worker that discovers and stores data anomalies",
    packages=find_packages(exclude=('tests',)),
    install_requires=[
        'Flask==1.1.4',
        'Flask-Cors==3.0.10',
        'Flask-Login==0.5.0',
        'Flask-WTF==0.14.3',
        'requests==2.22.0',
        'psycopg2-binary==2.8.6',
        'click==7.1.2',
        'scipy==1.7.0',
        'sklearn==0.0',
        'numpy==1.19.5', 
    ],
    entry_points={
        'console_scripts': [
            'insight_worker_start=workers.insight_worker.runtime:main',
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
