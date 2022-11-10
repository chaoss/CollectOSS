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
        "alembic==1.8.1", # 1.8.1
        "coloredlogs==15.0", # 15.0.1
        "Beaker==1.11.0", # 1.11.0
        "SQLAlchemy==1.3.23", # 1.4.40
        "itsdangerous==2.0.1", # 2.1.2
        "Jinja2==3.0.2", # 3.1.2
        "Flask==2.0.2", # 2.2.2
        "Flask-Cors==3.0.10",
        "Flask-Login==0.5.0",
        "Flask-WTF==1.0.0",
        "pandas==1.3.5", # 1.4.3
        "numpy==1.21", # 1.23.2
        "requests==2.28.0", # 2.28.1
        "psycopg2-binary==2.9.3", #2.9.3 what is pscopg-binary 3.0.16
        "click==8.0.3", # 8.1.3
        "psutil==5.8.0", # 5.9.1
        "gunicorn==20.1.0", # 20.1.0
        "six==1.15.0", # 1.16.0
        "bokeh==2.0.2", # 2.4.3
        "selenium==3.141.0",# 4.4.3
        "dask>=2021.6.2", # 2022.8.1
        "cloudpickle >= 0.2.2", # 2.1.0
        "fsspec >= 0.6.0", # 2022.7.1
        "toolz >= 0.8.2", # 0.12.0
        "partd >= 0.3.10", # 1.3.0
        "distributed >= 2021.03.0", # 2022.8.1
        "nltk==3.6.6", # 3.7
        "h5py~=3.6.0", # 3.7
        "scipy==1.7.3", # 1.9.0
        "blinker==1.4", # 1.5
        "protobuf<3.22", # 4.21.5
        "slack==0.0.2", # 0.0.2
        "boto3==1.17.57", # 1.24.56
        "toml", # 0.10.2
        "mistune==0.8.4", # 2.0.4
        "pyYaml", # 6.0
        "redis==4.3.3", # 4.3.4
        "XlsxWriter==1.3.7", # 3.0.3
        "celery==5.2.7", # 5.2.7
        "httpx==0.23.0", # 0.23.0
        "eventlet==0.33.1", 
        "flower==1.2.0",
        "tornado==6.1", # added because it sometimes errors when tornado is not 6.1 even though nothing we install depends on it
        "pylint==2.15.5"
    ],
    extras_require={
        "dev": [
            "tox==3.24.4", # 3.25.1
            "pytest==6.2.5", # 7.1.2
            "toml >= 0.10.2", # 0.10.2
            "ipdb==0.13.9", # 0.13.9
            "sphinx==4.2.0", # 5.1.1
            "sphinx_rtd_theme==1.0.0", # 1.0.0
            "sphinxcontrib-openapi==0.7.0", # 0.7.0
            "sphinxcontrib-redoc==1.6.0", # 1.6.0
            "docutils==0.17.1" # 0.19
        ]
    },
    entry_points={
        "console_scripts": [
            "augur=augur.application.cli._multicommand:run"
        ],
    }
)
