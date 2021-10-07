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
    name="clustering_worker",
    version="0.0.1",
    url="https://github.com/chaoss/augur",
    license='MIT',
    author="Sarit Adhikari",
    author_email="sarit.adhikari@gmail.com",
    description="worker to cluster repository based on messages on issues and pull requests ",
    packages=find_packages(),
    install_requires=[
        'Flask==1.1.4',
        'Flask-Cors==3.0.10',
        'Flask-Login==0.5.0',
        'Flask-WTF==0.14.3',
        'requests==2.22.0',
        'psycopg2-binary==2.8.6',
        'sklearn==0.0',
        'numpy==1.19.5',
        'nltk==3.5',
        'seaborn==0.11.1',
        'pandas==1.3.2',
        'matplotlib==3.3.4'
    ],
    entry_points={
        'console_scripts': [
            'clustering_worker_start=workers.clustering_worker.runtime:main',
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
