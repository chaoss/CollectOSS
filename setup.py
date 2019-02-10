'''
SPDX-License-Identifier: MIT

Install augur package with pip.
'''
import fastentrypoints
from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get global metadata
exec(open("augur/metadata.py").read())

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='augur',
    version=__version__,
    include_package_data=True,
    description='Library/Server for data related to the health and sustainability of OSS',
    long_description=long_description,
    url='https://github.com/chaoss/augur',
    author='Derek Howard',
    author_email='derek@howderek.com',
    packages=find_packages(),
    license='MIT',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Version Control',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='ghtorrent github api data science',
    install_requires=[
        'cython', 'protobuf', 'ipython', 'setuptools-git', 'beautifulsoup4', 'flask', 'flask-cors',
        'PyMySQL', 'requests', 'python-dateutil', 'sqlalchemy', 'pandas', 'pytest', 'PyGithub', 
        'GitPython', 'gunicorn', 'traitlets', 'coloredlogs', 'tldextract', 'beaker', 'lockfile',
        'werkzeug', 'flask-login', 'wtforms', 'Flask-WTF', 'alembic', 'colored',
        'prompt_toolkit', 'click', 'psycopg2-binary'],
    extras_require={
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },
    entry_points={
        'console_scripts': [
            'augur=augur.runtime:run',
        ],
    },
)
