#!/bin/bash

PS3="
Please type the number corresponding to your selection and then press the Enter/Return key.
Your choice: "

if [[ ! -e augur.config.json ]]; then
  echo "** No config file was found. Starting config creation process. **"

  echo
  echo "**********************************"
  echo "Setting up the database configuration..."
  echo "**********************************"
  echo
  echo "Would you like to enter your database credentials at the command line or on a web page?"
  select credential_setup_method in "Command Line" "Webpage"
  do
    case $credential_setup_method in
      "Command Line" )
          util/scripts/install/setup_db.sh
          break
        ;;
      "Webpage" )
          echo "Continuing installation via webpage..."
          pwd
          cd util/scripts/install/webserver
          python server.py
          cd ..
          python make_config.py
          rm temp.config.json
          cd ../../..
          pwd
          break
        ;;
    esac
  done
else
  echo "** Config file was found. Resuming installation... **"
fi
