"""
SPDX-License-Identifier: MIT

Install augur package with pip.
"""
from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="augur",
    version="0.11.0",
    include_package_data=True,
    description="Library/Server for data related to the health and sustainability of OSS",
    long_description=long_description,
    url="https://github.com/chaoss/augur",
    author="Derek Howard",
    author_email="derek@howderek.com",
    packages=find_packages(),
    license="MIT",
    classifiers=[
        "Development Status :: 1 - Planning",
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
        "pandas",
        "requests",
        "flask_cors",
        "flask_wtf",
        "psycopg2-binary",
        "click",
        "gunicorn==19.9.0",
        "six>=1.14.0"
    ],
    extras_require={
        "dev": ["tox", "pytest", "ipdb", "sphinx","sphinx_rtd_theme"],
        "xlsx": ["xlsxwriter"]
    },
    entry_points={
        "console_scripts": [
            "augur=augur.runtime:run"
        ],
    }
)
