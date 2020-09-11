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

echo "Installing the backend and its dependencies..."
scripts/install/backend.sh $target > logs/install/backend.log 2>&1
echo "Done!"

echo "Installing workers and their dependencies..."
scripts/install/workers.sh $target > logs/install/workers.log 2>&1
echo "Done!"

if [[ ! -e augur.config.json ]]; then
  echo "No config file found. Generating..."
  scripts/install/config.sh
  echo
else
  read -r -p "We noticed you have a config file already. Would you like to overwrite it with a new one? [Y/n] " response
  case "$response" in
      [yY][eE][sS]|[yY])
          echo "Generating a config file..."
          scripts/install/config.sh $target
          echo
          ;;
      *)
          echo "Skipping config generation process and resuming installation..."
          echo
          ;;
  esac
fi

scripts/install/frontend.sh
scripts/install/api_key.sh

echo "**********************************"
echo "***** INSTALLATION COMPLETE *****"
echo "**********************************"
