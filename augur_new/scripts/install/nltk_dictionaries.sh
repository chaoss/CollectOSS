#!/bin/bash
set -eo pipefail

echo "MACHINE LEARNING WORKER NOTE: Next, you will be asked to install some wordlists for the natural language processing parts of Augur.  Please be advised that the machine learning workers, including the clustering worker, discourse worker, messsage_analysis_worker, pull_request_analysis_worker, and the LSTM model of the insight_worker will not function fully without these lists."

read -r -p "Would you like to install required NLTK word lists for machine learning workers? [Y/n] " response
case "$response" in
  [yY][eE][sS]|[yY])
    echo "Installing..."
    python -m nltk.downloader stopwords 
    python -m nltk.downloader punkt                
    python -m nltk.downloader popular 
    python -m nltk.downloader universal_tagset 
    echo "Done!"
    ;;
  *)
    echo "Skipping NLTK Word Vector dependencies. Please be advised that the machine learning workers, including the clustering worker, discourse worker, messsage_analysis_worker, pull_request_analysis_worker, and the LSTM model of the insight_worker will not function fully without these lists."
    ;;

esac


echo "*************************************************"
echo "***** NLTK DICTIONARY INSTALLATION COMPLETE *****"
echo "*************************************************"
