#!/bin/bash
set -eo pipefail

scripts/install/checks.sh
if [[ $? -ne 0 ]]; then
  exit 1
fi

target=${1-prod}

if [[ $target == *"dev"* ]]; then
  echo
  echo "*****INSTALLING FOR DEVELOPMENT*****"
  echo
else
  echo
  echo "*****INSTALLING FOR PRODUCTION*****"
  echo
fi

scripts/install/backend.sh $target 2>&1 | tee logs/backend-install.log
echo "Done!"

scripts/install/workers.sh $target 2>&1 | tee logs/workers-install.log
echo "Done!"

if [[ ! -e augur.config.json && ! -e $HOME/.augur/augur.config.json ]]; then
  echo "No config file found. Generating..."
  scripts/install/config.sh $target
else
  read -r -p "We noticed you have a config file already. Would you like to overwrite it with a new one? [Y/n] " response
  case "$response" in
      [yY][eE][sS]|[yY])
          echo "Generating a config file..."
          scripts/install/config.sh $target
          ;;
      *)
          ;;
  esac
fi

scripts/install/frontend.sh
scripts/install/api_key.sh

echo "MACHINE LEARNING WORKER NOTE: Next, you will be asked to install some wordlists for the natural language processing parts of Augur.  Please be advised that the machine learning workers, including the clustering worker, discourse worker, messsage_analysis_worker, pull_request_analysis_worker, and the LSTM model of the insight_worker will not function fully without these lists."

read -r -p "Would you like to install required NLTK word lists for machine learning workers? [Y/n] " response
case "$response" in
  [yY][eE][sS]|[yY])
    echo "Installing... aritificial intelligence, machine learning. deep learning, and crocheting libraries and wordlists"
    scripts/install/nltk_dictionaries.sh
    echo "Done!"
    ;;
  *)
    echo "Skipping NLTK Word Vector dependencies. Please be advised that the machine learning workers, including the clustering worker, discourse worker, messsage_analysis_worker, pull_request_analysis_worker, and the LSTM model of the insight_worker will not function fully without these lists."
    ;;
esac


echo "**********************************"
echo "***** INSTALLATION COMPLETE *****"
echo "**********************************"
