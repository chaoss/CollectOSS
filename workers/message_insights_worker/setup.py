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
        'Flask==1.1.4',
        'Flask-Cors==3.0.10',
        'Flask-Login==0.5.0',
        'Flask-WTF==0.14.3',
        'requests==2.22.0',
        'psycopg2-binary==2.8.6',
        'click==7.1.2',
        'scipy==1.4.1',
        'sklearn==0.0',
        'numpy==1.19.5',
        'nltk==3.5',
        'pandas==1.1.3',
        'gensim==3.8.3',
        'emoji==1.2.0',
        'Keras==2.4.3',
        'Keras-Preprocessing==1.1.2',
        'tensorflow==2.5.0',
        'h5py==2.10.0',
        'scikit-image==0.18.1',
        'joblib==1.0.1',
        'xgboost==0.90',
        'bs4==0.0.1',
        'xlrd==2.0.1'
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
