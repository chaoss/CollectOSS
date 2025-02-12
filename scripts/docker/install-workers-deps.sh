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

# Note this
CURRENT_DIR=$PWD;

# Install scc
SCC_DIR="$HOME/scc"
echo "Cloning Sloc Cloc and Code (SCC) to generate value data ..."
git clone https://github.com/boyter/scc "$SCC_DIR"
cd $SCC_DIR
go build;
echo "scc build done"
cd $CURRENT_DIR

# Install scorecard
SCORECARD_DIR="$HOME/scorecard"
echo "Cloning OSSF Scorecard to generate scorecard data ..."
git clone https://github.com/ossf/scorecard $SCORECARD_DIR
cd $SCORECARD_DIR
go build;
echo "scorecard build done"
cd $CURRENT_DIR
