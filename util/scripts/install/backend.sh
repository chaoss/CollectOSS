#!/bin/bash

echo
echo "**********************************"
echo "Installing backend dependencies..."
echo "**********************************"
echo

pip install xlsxwriter setuptools;
pip install sphinx rtd_sphinx_theme;
npm install apidoc;
pip install -e .; 
