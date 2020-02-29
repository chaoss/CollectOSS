#!/bin/bash
set -euo pipefail

PS3="
Please type the number corresponding to your selection and then press the Enter/Return key.
Your choice: "

# check for python, pip, and a virtual environment being active
# if the script exit value != 0 indicating some failure, then stop
scripts/install/checks.sh

if [[ $? -ne 0 ]]; then
  exit 1
fi

if [[ ! -d logs ]]; then
    mkdir logs
fi

target=${1-prod}

echo "Installing the backend and its dependencies..."
scripts/install/backend.sh $target > logs/backend-installation.log 2>&1
echo "Done!"

echo "Installing workers and their dependencies..."
scripts/install/workers.sh $target > logs/workers-installation.log 2>&1
echo "Done!"

if [[ $target == *"dev"* ]]; then
  echo "Generating documentation..."
  scripts/install/api_docs.sh > logs/api-doc-generation.log 2>&1
  echo "Done!"
fi

echo "Generating a config file..."
scripts/install/config.sh > logs/config-generation.log 2>&1
echo "Done!"

echo
echo "Would you like to install Augur's frontend dependencies?"
echo
select choice in "y" "n"
do
  case $choice in
    "y" )
      scripts/install/frontend.sh > logs/frontend-installation.log 2>&1
      break
      ;;
    "n" )
      echo "Skipping frontend dependencies..."
      break
      ;;
   esac
done

echo "**********************************"
echo "*** INSTALLATION COMPLETE ***"
echo
echo "Documentation found here at:"
echo "https://oss-augur.readthedocs.io/en/master/"
echo "**********************************"
