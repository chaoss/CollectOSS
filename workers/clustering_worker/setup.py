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
        'Flask==2.0.2',
        'Flask-Cors==3.0.10',
        'Flask-Login==0.5.0',
        'Flask-WTF==1.0.0',
        'requests==2.27.1',
        'psycopg2-binary==2.9.3',
        'sklearn==0.0',
        'numpy==1.21.0',
        'nltk==3.6.6',
        'seaborn==0.11.1',
        'pandas==1.3.5',
        'matplotlib==3.5.1'
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
