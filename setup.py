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
        "Programming Language :: Python :: 3.6",
    ],
    install_requires=[
        "coloredlogs",
        "beaker",
        "sqlalchemy",
        "flask_login",
        "flask",
        "pandas==1.0.5",
        "numpy<1.19.0,>=1.16.0",
        "requests",
        "flask_cors",
        "flask_wtf",
        "psycopg2-binary",
        "click",
        "psutil",
        "gunicorn",
        "six>=1.14.0",
        "bokeh",
        "selenium"
    ],
    extras_require={
        "dev": [
            "tox",
            "pytest",
            "ipdb",
            "sphinx",
            "sphinx_rtd_theme",
            "sphinxcontrib-openapi",
            "sphinxcontrib-redoc",
            "docutils==0.15"
        ]
    },
    entry_points={
        "console_scripts": [
            "augur=augur.cli._multicommand:run"
        ],
    }
)
