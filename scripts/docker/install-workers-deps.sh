#!/bin/bash
set -x
OLD=$(pwd)
for i in $(find . | grep -i setup.py);
do
	
	cd $(dirname $i)
	/opt/venv/bin/pip install .
	cd $OLD
done

# install nltk
/opt/venv/bin/python -m nltk.downloader all
