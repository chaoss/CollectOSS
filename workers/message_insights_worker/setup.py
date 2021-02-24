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
    name="message_insights_worker",
    version="0.0.0",
    url="https://github.com/chaoss/augur",
    license='MIT',
    author="Augur Team",
    author_email="akshblr555@gmail.com",
    description="Message Insights worker that detects novel messages & analyzes sentiment from issue, PR messages",
    packages=find_packages(),
    install_requires=[
        'flask',
        'requests',
        'psycopg2-binary',
        'sklearn',
        'nltk',
        'pandas',
        'numpy',
        'gensim',
        'scipy',
        'emoji',
        'keras',
        'tensorflow==2.2.0',
        'h5py',
        'scikit-image',
        'joblib',
        'xgboost==0.90',
        'bs4', 
        'xlrd'
    ],
    entry_points={
        'console_scripts': [
            'message_insights_worker_start=workers.message_insights_worker.runtime:main',
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
