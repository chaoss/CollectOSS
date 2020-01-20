#!/bin/bash

PS3="
Please type the number corresponding to your selection and then press the Enter/Return key.
Your choice: "

function get_api_key_and_repo_path() {
  echo
  echo "Additionally, you'll need to provide a valid GitHub API key."
  echo "** This is required for Augur to gather data ***"
  read -p "GitHub API Key: " github_api_key
  echo

  echo
  echo "The Facade data collection worker needs to clone repositories to run its analysis."
  echo "Would you like to use an existing directory, or create a new one?"
  select create_facade_repo in "Create a new directory" "Use an existing directory"
  do
    case $create_facade_repo in
      "Create a new directory" )
          echo "** You MUST use an absolute path. **"
          read -p "Desired directory name: " facade_repo_directory
          if [[ -d "$facade_repo_directory" ]]; then
            echo "That directory already exists. Continuing..."
          else
            mkdir "$facade_repo_directory"
            echo "Directory created."
          fi
          break
        ;;
      "Use an existing directory" )
          echo "** You MUST use an absolute path. **"
          read -p "Facade repo path: " facade_repo_directory

          while [[ ! -d "$facade_repo_directory" ]]; do
            echo "That directory does not exist."
            echo "** You MUST use an absolute path. **"
            read -p "Facade repo path: " facade_repo_directory
          done

          break
        ;;
    esac
  done

  [[ "${facade_repo_directory}" != */ ]] && facade_repo_directory="${facade_repo_directory}/"

}

function set_remote_db_credentials() {

  read -p "Database: " db_name
  read -p "Host: " host
  read -p "Port: " port
  read -p "User: " db_user
  read -p "Password: " password

  get_api_key_and_repo_path

  save_credentials
}

function set_local_db_credentials() {

  read -p "Database: " db_name
  read -p "User: " db_user
  read -p "Port: " port
  read -p "Password: " password

  host="localhost"

  get_api_key_and_repo_path

  save_credentials
}

function save_credentials() {

  echo
  echo "**********************************"
  echo "Generating configuration file..."
  echo "**********************************"
  echo

  augur configure generate --db_name $db_name --db_host $host --db_port $port --db_user $db_user --db_password $password --github_api_key $github_api_key --facade_repo_directory $facade_repo_directory
  echo $host:$port:$db_name:$db_user:$password >> ~/.pgpass 
  chmod 0600 ~/.pgpass 

}

function create_db_schema() {

    psql -h $host -d $db_name -U $db_user -p $port -a -w -f persistence_schema/1-schema.sql
    psql -h $host -d $db_name -U $db_user -p $port -a -w -f persistence_schema/2-augur_data.sql
    psql -h $host -d $db_name -U $db_user -p $port -a -w -f persistence_schema/3-augur_operations.sql
    psql -h $host -d $db_name -U $db_user -p $port -a -w -f persistence_schema/4-spdx.sql
    psql -h $host -d $db_name -U $db_user -p $port -a -w -f persistence_schema/5-seed-data.sql
    psql -h $host -d $db_name -U $db_user -p $port -a -w -f persistence_schema/6-schema_update_8.sql
    psql -h $host -d $db_name -U $db_user -p $port -a -w -f persistence_schema/7-schema_update_9.sql

    psql -h $host -d $db_name -U $db_user -p $port -a -w -c "UPDATE augur_data.settings SET VALUE = '$facade_repo_directory' WHERE setting='repo_directory';"
    echo "Schema created"

    echo "Would you like to load your database with some sample data provided by Augur?"
    select should_load_db in "Yes" "No"
    do
      case $should_load_db in
        "Yes" )
          "Loading database with sample dataset."
          persistence_schema/db_load.sh $host $db_name $db_user $port
          break
          ;;
        "No" )
          echo "Database will not be loaded. Resuming installation..."
          break
          ;;
      esac
    done
}

echo "If you need to install Postgres, the downloads can be found here: https://www.postgresql.org/download/"
echo
install_locally="Would you like create the Augur database, user and schema LOCALLY?"
install_remotely="Would you like to add the Augur schema to an already created Postgres 10 or 11 database (local or remote)?"
already_installed="Would you like to connect to a database already configured with Augur's schema? "
echo

select install_location in "$install_locally" "$install_remotely" "$already_installed"
do
  case $install_location in
    $install_locally )
        echo "Please set the credentials for your database."
        set_local_db_credentials
        psql -h $host -p $port -a -w -c "CREATE DATABASE $db_name;"
        psql -h $host -p $port -a -w -c "CREATE USER $db_user WITH ENCRYPTED PASSWORD '$password';"
        psql -h $host -p $port -a -w -c "ALTER DATABASE $db_name OWNER TO $db_user;"
        psql -h $host -p $port -a -w -c "GRANT ALL PRIVILEGES ON DATABASE $db_name TO $db_user;"
        echo "DB created"
        create_db_schema
        break
      ;;
    $install_remotely )
        echo "Please set the credentials for your database."
        set_remote_db_credentials
        # https://www.youtube.com/watch?v=rs9wuaVV33I
        create_db_schema
        break
      ;;
    $already_installed )
        echo "Please enter the credentials for your database."
        set_remote_db_credentials
        break
      ;;
  esac
done



