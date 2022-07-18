#!/bin/bash
set -eo pipefail

function get_api_key() {
    api_key=$(augur db generate-api-key)
    echo
    echo "****** YOUR AUGUR API KEY ******"
    echo $api_key
    echo
    echo "You will need this API key to access the endpoints for "
    echo "adding repos to the database. Make sure to save it somewhere! "
    echo "If you do lose it, run 'augur db get-api-key' on the CLI."
    echo "Any old Augur API keys you may have will no longer work."
    echo "****************************************************************"
    echo
}

existing_api_key=$(augur db get-api-key)
echo
if [[ $existing_api_key != *"invalid_key"* ]]; then
  read -r -p "We noticed you have an Augur API key already. Would you like to overwrite it with a new one? [Y/n] " response
  case "$response" in
      [yY][eE][sS]|[yY])
          echo
          get_api_key
          ;;
      *)
          ;;
  esac
else
    get_api_key
fi

