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
  util/scripts/install/setup_db.sh
else
  echo "** Config file was found. Resuming installation... **"
fi
