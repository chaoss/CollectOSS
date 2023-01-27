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
# taken from ./scripts/install/nltk_dictionaries.sh
for i in stopwords punkt popular universal_tagset ; do
	/opt/venv/bin/python -m nltk.downloader $i
done
