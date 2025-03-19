#!/bin/bash
set -x

# Note this
CURRENT_DIR=$PWD;
# 18GB
# Install scc
SCC_DIR="$HOME/scc"
echo "Cloning Sloc Cloc and Code (SCC) to generate value data ..."
# this needs to be done from source. the latest version doesnt seem to exist on the package repo
# however, the latest version (v3.5.0) requires bumping the golang version in the Dockerfile
git clone --depth 1 --branch v3.4.0 https://github.com/boyter/scc "$SCC_DIR"
cd $SCC_DIR
go build;
echo "scc build done"
cd $CURRENT_DIR
# 18GB

# Install scorecard
SCORECARD_DIR="$HOME/scorecard"
echo "Cloning OSSF Scorecard to generate scorecard data ..."
# lock version to prevent future issues if the golang version is bumped
git clone --depth 1 --branch v5.1.1 https://github.com/ossf/scorecard $SCORECARD_DIR
cd $SCORECARD_DIR
go build;
echo "scorecard build done"
cd $CURRENT_DIR

# 16GB