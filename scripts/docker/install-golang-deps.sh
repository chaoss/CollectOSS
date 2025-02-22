#!/bin/bash
set -x

# Note this
CURRENT_DIR=$PWD;
# 18GB
# Install scc
SCC_DIR="$HOME/scc"
echo "Cloning Sloc Cloc and Code (SCC) to generate value data ..."
git clone https://github.com/boyter/scc "$SCC_DIR"
cd $SCC_DIR
go build;
echo "scc build done"
cd $CURRENT_DIR
# 18GB

# Install scorecard
SCORECARD_DIR="$HOME/scorecard"
echo "Cloning OSSF Scorecard to generate scorecard data ..."
git clone https://github.com/ossf/scorecard $SCORECARD_DIR
cd $SCORECARD_DIR
go build;
echo "scorecard build done"
cd $CURRENT_DIR

# 16GB