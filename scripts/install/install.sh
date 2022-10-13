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

scripts/install/backend.sh $target 2>&1 | tee logs/backend-install.log
echo "Done!"

scripts/install/workers.sh $target 2>&1 | tee logs/workers-install.log
echo "Done!"

scripts/install/nltk_dictionaries.sh


function create_db_config() {
    echo "Enter the database credentials to your database. This will create db.config.json"
    read -p "User: " db_user
    read -s -p "Password: " password
    echo
    read -p "Host: " host
    read -p "Port: " port
    read -p "Database: " db_name

    echo -e "{\n\t\"user\":\"${db_user}\", \n\t\"password\":\"${password}\", \n\t\"host\":\"${host}\", \n\t\"port\":\"${port}\", \n\t\"database_name\":\"${db_name}\"\n}" > db.config.json
}

# if there is no db.config.json or the AUGUR_DB environment variable is not set 
#then create prompt the user for db credentials and make a db.config.json file

if [[ -z "${AUGUR_DB}" ]]
then

    FILE=db.config.json
    if [[ -f "$FILE" ]]
    then
        echo "Your db.config.json file contents"
        cat $FILE
        echo
        echo
        read -r -p "You already have a db.config.json (shown above). Would you like to override it? [y/N] " response

        case "$response" in [yY][eE][sS]|[yY])
            create_db_config
        esac 
    else 
        create_db_config
    fi
fi


connection_status=$(augur db test-connection)

if [[ "$connection_status" =~ "You are not connect to the internet." ]]; then
    echo
    echo "ERROR: No internet connection. Please check internet connection"
    echo
    exit 0
fi
if [[ "$connection_status" =~ "ERROR: connecting to database" ]]; then
    echo
    echo "ERROR: Could not connect to database. Please check database configuration"
    echo
    exit 0
fi

echo
echo "Creating database schema"
augur db create-schema 
echo "Schema successfully created!"


scripts/install/config.sh $target
# scripts/install/api_key.sh

augur db check-pgpass


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


