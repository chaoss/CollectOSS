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
        'alabaster==0.7.12',
        'alembic==1.2.1',
        'appnope==0.1.0',
        'atomicwrites==1.3.0',
        'attrs==19.3.0',
        'Babel==2.7.0',
        'backcall==0.1.0',
        'Beaker==1.11.0',
        'beautifulsoup4==4.8.1',
        'certifi==2019.9.11',
        'chardet==3.0.4',
        'Click==7.0',
        'colored==1.4.0',
        'coloredlogs==10.0',
        'Cython==0.29.13',
        'decorator==4.4.1',
        'Deprecated==1.2.6',
        'docutils==0.15.2',
        'Flask==1.1.1',
        'Flask-Cors==3.0.8',
        'Flask-Login==0.4.1',
        'Flask-WTF==0.14.2',
        'gitdb2==2.0.6',
        'GitPython==3.0.4',
        'gunicorn==19.9.0',
        'humanfriendly==4.18',
        'idna==2.8',
        'imagesize==1.1.0',
        'importlib-metadata==0.23',
        'ipdb==0.12.2',
        'ipython==7.9.0',
        'ipython-genutils==0.2.0',
        'itsdangerous==1.1.0',
        'jedi==0.15.1',
        'Jinja2==2.10.3',
        'lockfile==0.12.2',
        'Mako==1.1.0',
        'MarkupSafe==1.1.1',
        'more-itertools==7.2.0',
        'numpy==1.17.3',
        'packaging==19.2',
        'pandas==0.25.2',
        'parso==0.5.1',
        'pexpect==4.7.0',
        'pickleshare==0.7.5',
        'pluggy==0.13.0',
        'prompt-toolkit==2.0.10',
        'protobuf==3.10.0',
        'psycopg2-binary==2.8.4',
        'ptyprocess==0.6.0',
        'py==1.8.0',
        'PyGithub==1.44',
        'Pygments==2.4.2',
        'PyJWT==1.7.1',
        'PyMySQL==0.9.3',
        'pyparsing==2.4.2',
        'pytest==5.2.2',
        'python-dateutil==2.8.0',
        'python-editor==1.0.4',
        'pytz==2019.3',
        'requests==2.22.0',
        'requests-file==1.4.3',
        'setuptools-git==1.2',
        'six==1.12.0',
        'smmap2==2.0.5',
        'snowballstemmer==2.0.0',
        'soupsieve==1.9.4',
        'Sphinx==2.2.1',
        'sphinxcontrib-applehelp==1.0.1',
        'sphinxcontrib-devhelp==1.0.1',
        'sphinxcontrib-htmlhelp==1.0.2',
        'sphinxcontrib-jsmath==1.0.1',
        'sphinxcontrib-qthelp==1.0.2',
        'sphinxcontrib-serializinghtml==1.1.3',
        'SQLAlchemy==1.3.10',
        'tldextract==2.2.2',
        'traitlets==4.3.3',
        'urllib3==1.25.6',
        'wcwidth==0.1.7',
        'Werkzeug==0.16.0',
        'wrapt==1.11.2',
        'WTForms==2.2.1',
        'XlsxWriter==1.2.2',
        'zipp==0.6.0'
    ],
    extras_require={
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },
    entry_points={
        'console_scripts': [
            'augur=augur.runtime:run',
            'augur_run=augur.cli.run:run'
        ],
    },
)
