'''
SPDX-License-Identifier: MIT

Install ghdata package with pip.
'''

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ghdata',
    version='0.2.2',
    description='Library/Server for data related to the health and sustainability of GitHub projects',
    long_description=long_description,
    url='https://github.com/OSSHealth/ghdata',
    author='Derek Howard',
    author_email='derek@howderek.com',
	packages=['ghdata'],
	package_dir={'ghdata': 'ghdata'},
    license='MIT',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Version Control',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='ghtorrent github api data science',
    install_requires=['flask', 'flask-cors', 'PyMySQL', 'requests', 'python-dateutil', 'sqlalchemy', 'pandas', 'pytest', 'PyGithub', 'pyevent'],
    extras_require={
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },
    entry_points={
        'console_scripts': [
            'ghdata=ghdata.server:run',
        ],
    },
)
