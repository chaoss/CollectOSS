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
        'flask',
        'requests',
        'psycopg2-binary',
        'sklearn',
        'numpy',
        'nltk',
        'seaborn',
        'pandas',
        'matplotlib'
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
