#!/bin/bash
set -eo pipefail

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

scripts/install/frontend.sh

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
