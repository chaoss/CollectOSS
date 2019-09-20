#!/bin/bash

PS3="
Please type the number corresponding to your selection and then press the Enter/Return key.
Your choice: "

echo
echo "**********************************"
echo "Setting up the database configuration..."
echo "**********************************"
echo

function generate_config_file() {

  echo
  echo "**********************************"
  echo "Generating configuration file..."
  echo "**********************************"
  echo

  INSTALL_SCRIPT_HOME="util/scripts/install"
  cd $INSTALL_SCRIPT_HOME

  rm temp.config.json
  touch temp.config.json

  echo $1 > temp.config.json

  python make_config.py

  rm temp.config.json

  cd ../../.. #get back to augur root
}

function set_remote_db_credentials() {

  read -p "database: " database
  read -p "host: " host
  read -p "port: " port
  read -p "user: " user
  read -p "password: " password
  read -p "key: " key

  config="
  {
    \"database\": \"$database\",
    \"host\": \"$host\",
    \"port\": \"$port\",
    \"user\": \"$user\",
    \"password\": \"$password\",
    \"key\": \"$key\"
  }"

  # generate_config_file $config
}

function set_local_db_credentials() {

  read -p "database: " database
  read -p "user: " user
  read -p "port: " port
  read -p "password: " password
  read -p "key: " key

  config="
  {
    \"database\": \"$database\",
    \"host\": \"localhost\",
    \"port\": \"$port\",
    \"user\": \"$augur\",
    \"password\": \"$password\",
    \"key\": \"$key\"
  }"

  # generate_config_file $config
}

echo "If you need to install Postgres, the downloads can be found here: https://www.postgresql.org/download/"
echo
install_locally="Would you like to use a LOCAL Postgres 10 or 11 installation without the database already installed?"
install_remotely="Would you like to use a REMOTE Postgres 10 or 11 installation without the database already installed?"
already_installed="Would you like to use a pre-existing Postgres 10 or 11 installation with the Augur database ALREADY installed? "
SKIP="Skip this section"
echo

select install_location in "$install_locally" "$install_remotely" "$already_installed" "$SKIP"
do
  case $install_location in
      $SKIP )
      echo
      echo "Skipping database configuration..."
      echo
      break
    ;;
    $install_locally )
        echo "Please set the credentials for your database."
        set_local_db_credentials
        psql -c "create database $database;"
        psql -c "create user $user with encrypted password '$password';"
        psql -c "alter database $database owner to $user;"
        psql -c "grant all privileges on database $database to $user;"
        psql -h "localhost" -d $database -U $user -p $port -a -w -f augur/persistence_schema/0-all.sql
        break
      ;;
    $install_remotely )
        echo "Please set the credentials for your database."
        set_remote_db_credentials
        psql -h $host -p $port -c "create database $database;"
        psql -h $host -p $port -c "create user $user with encrypted password '$password';"
        psql -h $host -p $port -c "alter database $database owner to $user;"
        psql -h $host -p $port -c "grant all privileges on database $database to $user;"
        psql -h $host -d $database -U $user -p $port -a -w -f augur/persistence_schema/0-all.sql
        break
      ;;
    $already_installed )
        echo "Please enter the credentials for your database."
        enter_db_credentials
        break
      ;;
  esac
done
