#!/bin/bash
set -eo pipefail

# check for python, pip, and a virtual environment being active
# if the script exit value != 0 indicating some failure, then stop
scripts/install/checks.sh

if [[ $? -ne 0 ]]; then
  exit 1
fi

if [[ ! -d logs ]]; then
    mkdir logs
fi

if [[ ! -d logs/install ]]; then
    mkdir logs/install
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

echo "Installing the backend and its dependencies..."
scripts/install/backend.sh $target > logs/install/backend.log 2>&1
echo "Done!"

echo "Installing workers and their dependencies..."
scripts/install/workers.sh $target > logs/install/workers.log 2>&1
echo "Done!"

if [[ ! -e augur.config.json ]]; then
  echo "** No config file found **"
  scripts/install/config.sh
else
  read -r -p "We noticed you have a config file already. Would you like to overwrite it with a new one? [Y/n] " response
  case "$response" in
      [yY][eE][sS]|[yY]) 
          echo "Generating a config file..."
          scripts/install/config.sh
          ;;
      *)
          echo "Skipping config generation process and resuming installation..."
          ;;
  esac
fi

if [[ $target == *"dev"* ]]; then
  read -r -p "Would you like to install Augur's frontend dependencies? [Y/n] " response
  case "$response" in
      [yY][eE][sS]|[yY]) 
        scripts/install/frontend.sh > logs/install/frontend.log 2>&1
        ;;
      *)
        echo "Skipping frontend dependencies..."
        ;;
  esac
else
  echo "Installing frontend dependencies..."
  scripts/install/frontend.sh > logs/frontend-installation.log 2>&1
fi

existing_api_key=$(augur db get-api-key)

if [[ $existing_api_key != *"invalid_key"* ]]; then
  read -r -p "We noticed you have an Augur API key already. Would you like to overwrite it with a new one? [Y/n] " response
  case "$response" in
      [yY][eE][sS]|[yY]) 
          scripts/install/api_key.sh
          ;;
      *)
          echo "Skipping API key generation process and resuming installation..."
          ;;
  esac
else
  scripts/install/api_key.sh
fi


echo "**********************************"
echo "*** INSTALLATION COMPLETE ***"
echo "https://oss-augur.readthedocs.io/en/master/"
echo "**********************************"
