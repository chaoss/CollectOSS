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


if [[ ! -e ~/nltk_wordlist_installations/stopwords.log ]]; then

    echo "You chose not to install NLTK dictionaries when you installed Augur, or installed augur after these workers were instroduced. They will be located in the \/usr/local/share directory, and can be removed following your rebuild."
    scripts/install/nltk_dictionaries.sh
fi
