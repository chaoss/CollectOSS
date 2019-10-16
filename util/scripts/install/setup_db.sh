#!/bin/bash

PS3="
Please type the number corresponding to your selection and then press the Enter/Return key.
Your choice: "

function generate_config_file() {

  echo
  echo "**********************************"
  echo "Generating configuration file..."
  echo "**********************************"
  echo

  INSTALL_SCRIPT_HOME="util/scripts/install"
  cd $INSTALL_SCRIPT_HOME

  if [[ -e temp.config.json ]]; then
    rm temp.config.json
  fi

  touch temp.config.json

  echo "$1" > temp.config.json

  python make_config.py

  rm temp.config.json

  cd ../../.. #get back to augur root
}

function get_github_api_key() {
  echo
  echo "You will also need your GitHub API key."
  read -p "GitHub API Key: " github_api_key
  echo
}

function set_remote_db_credentials() {

  read -p "Database: " database
  read -p "Host: " host
  read -p "Port: " port
  read -p "User: " db_user
  read -p "Password: " password

  get_github_api_key

  IFS='' read -r -d '' config <<EOF
    {
      "database": "$database",
      "host": "$host",
      "port": "$port",
      "user": "$db_user",
      "password": "$password",
      "key": "$github_api_key",
      "github_api_key": "$github_api_key"
    }
EOF

  save_credentials
}

function set_local_db_credentials() {

  read -p "Database: " database
  read -p "User: " user
  read -p "Port: " port
  read -p "Password: " password

  get_github_api_key

  IFS='' read -r -d '' config <<EOF
  {
    "database": "$database",
    "host": "localhost",
    "port": "$port",
    "user": "$db_user",
    "password": "$password",
    "key": "$github_api_key",
    "github_api_key": "$github_api_key"
  }
EOF

  save_credentials
}

function save_credentials() {

  generate_config_file "$config"

  echo $host:$port:$database:$db_user:$password >> ~/.pgpass 
  chmod 0600 ~/.pgpass 

}

echo "If you need to install Postgres, the downloads can be found here: https://www.postgresql.org/download/"
echo
install_locally="Would you like create the Augur database, user and schema LOCALLY?"
install_remotely="Would you like to add the Augur schema to a REMOTE Postgres 10 or 11 database?"
already_installed="Would you like to connect to a database already configured with Augur's schema? "
echo

select install_location in "$install_locally" "$install_remotely" "$already_installed"
do
  case $install_location in
    $install_locally )
        echo "Please set the credentials for your database."
        set_local_db_credentials
        psql -c "CREATE DATABASE $database;"
        psql -c "CREATE USER $db_user WITH ENCRYPTED PASSWORD '$password';"
        psql -c "ALTER DATABASE $database OWNER TO $db_user;"
        psql -c "GRANT ALL PRIVILEGES ON DATABASE $database TO $db_user;"
        psql -h "localhost" -d $database -U $db_user -p $port -a -w -f persistence_schema/1-schema.sql
        psql -h "localhost" -d $database -U $db_user -p $port -a -w -f persistence_schema/2-augur_data.sql
        psql -h "localhost" -d $database -U $db_user -p $port -a -w -f persistence_schema/3-augur_operations.sql
        psql -h "localhost" -d $database -U $db_user -p $port -a -w -f persistence_schema/4-spdx.sql
        psql -h "localhost" -d $database -U $db_user -p $port -a -w -f persistence_schema/5-seed-data.sql
        break
      ;;
    $install_remotely )
        echo "Please set the credentials for your database."
        set_remote_db_credentials
        # https://www.youtube.com/watch?v=rs9wuaVV33I
        psql -h $host -d $database -U $db_user -p $port -a -w -f persistence_schema/1-schema.sql
        psql -h $host -d $database -U $db_user -p $port -a -w -f persistence_schema/2-augur_data.sql
        psql -h $host -d $database -U $db_user -p $port -a -w -f persistence_schema/3-augur_operations.sql
        psql -h $host -d $database -U $db_user -p $port -a -w -f persistence_schema/4-spdx.sql
        psql -h $host -d $database -U $db_user -p $port -a -w -f persistence_schema/5-seed-data.sql

        break
      ;;
    $already_installed )
        echo "Please enter the credentials for your database."
        set_remote_db_credentials
        break
      ;;
  esac
done
