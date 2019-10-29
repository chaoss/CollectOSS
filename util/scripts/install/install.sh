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
util/scripts/install/backend.sh > logs/backend.log

# nomos scanner for dosocs
util/scripts/install/nomos.sh > logs/nomos.log 2>logs/nomos.err 

# workers
util/scripts/install/workers.sh >logs/workers.log 2>logs/workers.err 

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
