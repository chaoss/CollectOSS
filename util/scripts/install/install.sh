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

mkdir logs

# backend
util/scripts/install/backend.sh > logs/backend-install.log 2>logs/backend-install.err 
echo "Back End Installation Complete!  Check logs/backend-installer.log and logs/backend-installer.err"

# workers
util/scripts/install/workers.sh >logs/workers.log 2>logs/workers.err 
echo "Worker Installation Complete! Check logs/workers.log and logs/workers.err"

# docs
util/scripts/install/docs.sh

# config
util/scripts/install/config.sh



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
echo "**********************************"

echo "**********************************"
echo "Documentation found here:"
echo ""
echo "https://oss-augur.readthedocs.io/en/master/"
echo "**********************************"
