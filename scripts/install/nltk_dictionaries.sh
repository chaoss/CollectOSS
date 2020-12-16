#!/bin/bash
set -eo pipefail

echo "MACHINE LEARNING WORKER NOTE: Next, you will be asked to install some wordlists for the natural language processing parts of Augur.  Please be advised that the machine learning workers, including the clustering worker, discourse worker, messsage_analysis_worker, pull_request_analysis_worker, and the LSTM model of the insight_worker will not function fully without these lists."

read -r -p "Would you like to install required NLTK word lists for machine learning workers? [Y/n] " response
case "$response" in
  [yY][eE][sS]|[yY])
    echo "Installing..."
    mkdir ~/nltk_wordlist_installations
    python -m nltk.downloader stopwords -d /usr/local/share >> ~/nltk_wordlist_installations/stopwords.log
    python -m nltk.downloader punkt -d /usr/local/share  >> ~/nltk_wordlist_installations/punkt.log 
    python -m nltk.downloader popular -d /usr/local/share >> ~/nltk_wordlist_installations//popular.log
    python -m nltk.downloader universal_tagset -d /usr/local/share >> ~/nltk_wordlist_installations/universal_tagset.log
    echo "Done!"
    echo "Logs are stored in your home directory under 'nltk_wordlist_installations'." 
    ;;
  *)
    echo "Skipping NLTK Word Vector dependencies. Please be advised that the machine learning workers, including the clustering worker, discourse worker, messsage_analysis_worker, pull_request_analysis_worker, and the LSTM model of the insight_worker will not function fully without these lists."
    ;;
esac


echo "**********************************"
echo "***** NLTK DICTIONARY INSTALLATION  COMPLETE *****"
echo "**********************************"
