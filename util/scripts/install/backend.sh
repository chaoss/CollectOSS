#!/bin/bash

echo
echo "**********************************"
echo "Installing backend dependencies..."
echo "**********************************"
echo

pip install xlsxwriter setuptools; 
npm install apidoc;
python setup.py install;
pip install -e .; 
