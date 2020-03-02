#!/bin/bash

echo
echo "**********************************"
echo "Installing backend dependencies..."
echo "**********************************"
echo

pip install xlsxwriter setuptools sphinx;
pip install -e .; 
npm install apidoc;
