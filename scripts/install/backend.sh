#!/bin/bash
set -eo pipefail

echo "Installing backend dependencies..."
echo "**********************************"
echo

target=$1

if [[ $target == *"prod"* ]]; then
    pip install .
else
    pip install -e .[dev]
fi



read -r -p "Would you like to install required NLTK word lists for machine learning workers? [Y/n] " response
case "$response" in
  [yY][eE][sS]|[yY])
    echo "Installing..."
    python -m nltk.downloader stopwords > logs/stopwords.log
    python -m nltk.downloader punkt >logs/punkt.log
    python -m nltk.downloader popular >logs/popular.log
    python -m nltk.downloader universal_tagset >logs/universal_tagset.log
    echo "Done!"
    ;;
  *)
    echo "Skipping frontend dependencies..."
    ;;
esac
