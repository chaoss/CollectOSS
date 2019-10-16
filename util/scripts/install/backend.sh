#!/bin/bash

echo
echo "**********************************"
echo "Installing backend dependencies..."
echo "**********************************"
echo

rm -rf build/ dist/ docs/build/ workers/**/build/** workers/**/dist**
pip install xlsxwriter pip install setuptools; 
npm install apidoc;
pip install -e .; 
python setup.py install;
