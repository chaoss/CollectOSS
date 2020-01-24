#!/bin/bash

PS3="
Please type the number corresponding to your selection and then press the Enter/Return key.
Your choice: "

# check for python, pip, and a virtual environment being active
# if the script exit value != 0 indicating some failure, then stop
util/scripts/install/checks.sh

if [[ $? -ne 0 ]]; then
  exit 1
fi

if [[ ! -d logs ]]; then
    mkdir logs
fi

echo "Installing backend dependencies..."
util/scripts/install/backend.sh > logs/backend-install.log 2>logs/backend-install.err 
echo "Done!"

echo "Installing worker dependencies..."
util/scripts/install/workers.sh >logs/workers.log 2>logs/workers.err 
echo "Done!"

echo "Generating documentation..."
util/scripts/install/api_docs.sh
echo "Done!"

echo "Generating config..."
util/scripts/install/config.sh
echo "Done!"

echo
echo "Would you like to install Augur's frontend dependencies?"
echo
select choice in "y" "n"
do
  case $choice in
    "y" )
      util/scripts/install/frontend.sh
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
