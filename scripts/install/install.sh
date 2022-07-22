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

function create_db_config() {
    echo "Enter the database credentials to your database. This will create db.json"
    read -p "User: " db_user
    read -s -p "Password: " password
    echo
    read -p "Host: " host
    read -p "Port: " port
    read -p "Database: " db_name

    augur config-db init --user $db_user --password $password --host $host --port $port --database-name $db_name
}


# if there is no db.json or the AUGUR_DB environment variable is not set 
#then create prompt the user for db credentials and make a db.json file

if [[ -z "${AUGUR_DB}" ]]
then

    FILE=db.json
    if [[ -f "$FILE" ]]
    then
        echo "You db.json file contents"
        cat $FILE
        echo
        echo
        read -r -p "You already have a db.json (shown above). Would you like to override it? [y/N] " response

        case "$response" in [yY][eE][sS]|[yY])
            create_db_config
        esac 
    else 
        create_db_config
    fi
fi

scripts/install/backend.sh $target 2>&1 | tee logs/backend-install.log
echo "Done!"

echo
echo "Creating database schema"
augur db create-schema
echo "Schema successfully created!"


scripts/install/config.sh $target

echo "**********************************"
echo "***** INSTALLATION COMPLETE *****"
echo "**********************************"


# if [ $AUGUR_DB ]
# then
#     create_config
# else 
#     scripts/install/config.sh $target
# fi






# if [[ ! -e augur.config.json && ! -e $HOME/.augur/augur.config.json ]]; then
#   echo "No config file found. Generating..."
#   scripts/install/config.sh $target
# else
#   read -r -p "We noticed you have a config file already. Would you like to overwrite it with a new one? [Y/n] " response
#   case "$response" in
#       [yY][eE][sS]|[yY])
#           echo "Generating a config file..."
#           scripts/install/config.sh $target
#           ;;
#       *)
#           ;;
#   esac
# fi

# scripts/install/frontend.sh
# scripts/install/api_key.sh
# scripts/install/nltk_dictionaries.sh

# if [[ -e augur.config.json || -e $HOME/.augur/augur.config.json ]]; then
#   if [[ -e augur.config.json ]]; then
#     echo
#     echo "*****NOTE THIS INSTANCES PORT USE AND CONFIGURATION EDITING INFORMATION*****"
#     echo
#     echo "These are the ports used in your configuration. The last two are your externally exposed API ports." 
#     echo `cat augur.config.json | grep -E port`
#     echo "****************************************************************************"
#     echo "You can edit these ports in the augur.config.json file in this directory:"
#     echo 
#     echo `pwd`
#     echo
#     echo "****************************************************************************"
#     echo
#     echo "*****NOTE THIS INSTANCES PORT USE AND CONFIGURATION EDITING INFORMATION*****"
#     echo
#   else
#     echo
#     echo "*****NOTE THIS INSTANCES PORT USE AND CONFIGURATION EDITING INFORMATION*****"
#     echo
#     echo "These are the ports used in your configuration. The last two are your externally exposed API ports."
#     echo `cat $HOME/.augur/augur.config.json | grep -E port`
#     echo "****************************************************************************"
#     echo "You can edit these ports in the augur.config.json file in this directory:"
#     echo 
#     echo $HOME/.augur/
#     echo 
#     echo "****************************************************************************"
#     echo
#     echo
#     echo "*****NOTE THIS INSTANCES PORT USE AND CONFIGURATION EDITING INFORMATION*****"
#     echo
#   fi
# fi


