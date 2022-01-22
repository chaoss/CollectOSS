#SPDX-License-Identifier: MIT
"""
SPDX-License-Identifier: MIT

Install augur package with pip.
"""
from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

exec(open("metadata.py").read())

setup(
    name=__slug__,
    version=__version__,
    include_package_data=True,
    description=__short_description__,
    long_description=long_description,
    url=__url__,
    author="Derek Howard",
    author_email="derek@howderek.com",
    packages=find_packages(),
    license=__license__,
    classifiers=[
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Version Control",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
    ],
    install_requires=[
        "wheel",
        "coloredlogs==15.0",
        "Beaker==1.11.0",
        "SQLAlchemy==1.3.23",
        "itsdangerous==2.0.1",
        "Jinja2==3.0.2",
        "Flask==2.0.2",
        "Flask-Cors==3.0.10",
        "Flask-Login==0.5.0",
        "Flask-WTF==1.0.0",
        "pandas==1.3.5",
        "numpy==1.21",
        "requests==2.27.1",
        "psycopg2-binary==2.9.3",
        "click==8.0.3",
        "psutil==5.8.0",
        "gunicorn==20.1.0",
        "six==1.15.0",
        "bokeh==2.0.2",
        "selenium==3.141.0",
        "dask>=2021.6.2", 
        "cloudpickle >= 0.2.2",
        "fsspec >= 0.6.0",
        "toolz >= 0.8.2",
        "partd >= 0.3.10",
        "distributed >= 2021.03.0",
        "nltk==3.6.6",
        "h5py~=3.6.0",
        "scipy==1.7.3",
        "blinker==1.4",
        "protobuf > 3.6.0",
        "slack==0.0.2",
        "boto3==1.17.57",
        "toml",
        "mistune==0.8.4",
        "pyYaml"
    ],
    extras_require={
        "dev": [
            "tox==3.24.4",
            "pytest==6.2.5",
            "toml >= 0.10.2",
            "ipdb==0.13.9",
            "sphinx==4.2.0",
            "sphinx_rtd_theme==1.0.0",
            "sphinxcontrib-openapi==0.7.0",
            "sphinxcontrib-redoc==1.6.0",
            "docutils==0.17.1"
        ]
    },
    entry_points={
        "console_scripts": [
            "augur=augur.cli._multicommand:run"
        ],
    }
)
