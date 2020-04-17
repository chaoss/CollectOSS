#!/bin/bash
set -eo pipefail

api_key=$(augur db generate-api-key)
echo "****** YOUR AUGUR API KEY ******"
echo $api_key
echo
echo "You will need this API key to access the endpoints for "
echo "adding repos to the database. Make sure to save it somewhere! "
echo "If you do lose it, run 'augur db get-api-key' on the CLI."
echo "Any old Augur API keys you may have will no longer work."
echo "****************************************************************"
echo