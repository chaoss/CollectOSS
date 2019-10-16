#!/bin/bash

echo
echo "**********************************"
echo "Installing backend dependencies..."
echo "**********************************"
echo

rm -rf build/*; rm -rf dist/*; rm $VIRTUAL_ENV/bin/*worker*;
pip install pipreqs sphinx xlsxwriter; 
pip install -e .; 
pip install xlsxwriter; 
pip install ipykernel; 
python -m ipykernel install --user --name augur --display-name "Python (augur)"; 
npm install apidoc;
python setup.py install;
