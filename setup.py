'''
SPDX-License-Identifier: MIT

Install augur package with pip.
'''

from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='augur',
    version='0.4.1',
    include_package_data = True,
    description='Library/Server for data related to the health and sustainability of GitHub projects',
    long_description=long_description,
    url='https://github.com/OSSHealth/augur',
    author='Derek Howard',
    author_email='derek@howderek.com',
	packages=['augur'],
	package_dir={'augur': 'augur'},
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
    install_requires=['cython', 'ipdb', 'setuptools-git', 'beautifulsoup4', 'flask', 'flask-cors', 'PyMySQL', 'requests', 'python-dateutil', 'sqlalchemy', 'pandas', 'pytest', 'PyGithub', 'pyevent', 'gunicorn', 'datetime'],
    extras_require={
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },
    entry_points={
        'console_scripts': [
            'augur=augur.server:run',
        ],
    },
)
