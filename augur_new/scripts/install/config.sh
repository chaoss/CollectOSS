#!/bin/bash

PS3="
Please type the number corresponding to your selection and then press the Enter/Return key.
Your choice: "

target=$1

function get_api_key_and_repo_path() {
  echo
  echo "Please provide a valid GitHub API key."
  echo "For more information on how to create the key, visit:"
  echo "https://oss-augur.readthedocs.io/en/dev/getting-started/installation.html#backend"
  echo "** This is required for Augur to gather data ***"
  read -p "GitHub API Key: " github_api_key
  echo

  echo
  echo "Please provide a valid GitLab API key."
  echo "For more information on how to create the key, visit:"
  echo "https://oss-augur.readthedocs.io/en/dev/getting-started/installation.html#backend"
  echo "** This is required for Augur to gather data ***"
  read -p "GitLab API Key: " gitlab_api_key
  echo

  echo "The Facade data collection worker will clone repositories to this machine to run its analysis."
  echo "Would you like to clone to an existing directory, or create a new one?"

  select create_facade_repo in "Use an existing directory" "Create a new directory"
  do
    case $create_facade_repo in
      "Use an existing directory" )
          echo "** You MUST use an absolute path. Variable expansion is currently not supported.**"
          read -p "Facade repo path: " facade_repo_directory
          echo


          while [[ ! -d "$facade_repo_directory" ]]; do
            echo "That directory does not exist."
            read -p "Facade repo path: " facade_repo_directory
            echo
          done

          break
        ;;
      "Create a new directory" )
          echo "** You MUST use an absolute path. Variable expansion is currently not supported.**"
          read -p "Desired directory name: " facade_repo_directory
          echo

          if [[ -d "$facade_repo_directory" ]]; then
            echo "That directory already exists. Using the given directory."
            echo
          else
            mkdir "$facade_repo_directory"
            echo "Directory created."
            echo
          fi

          break
        ;;
    esac
  done

  [[ "${facade_repo_directory}" != */ ]] && facade_repo_directory="${facade_repo_directory}/"

}

function set_db_credentials() {

  install_locally=${1-false}

  read -p "Database: " db_name
  read -p "User: " db_user
  read -s -p "Password: " password
  echo

  if [[ $install_locally == 'false' ]]; then
    read -p "Host: " host
    read -p "Port: " port
  fi

  get_api_key_and_repo_path

  save_credentials
}


function save_credentials() {

  echo
  echo "**********************************"
  echo "Generating configuration file..."
  echo "**********************************"
  echo

  cmd=( augur config init --db_name $db_name --db_host $host --db_port $port --db_user $db_user --db_password $password --github_api_key $github_api_key --gitlab_api_key $gitlab_api_key --facade_repo_directory $facade_repo_directory )

  if [[ $target == *"dev"* ]]; then
    cmd+=( --write-to-src )
  fi

  "${cmd[@]}"

  augur config init-frontend
  augur db check-pgpass

}

function create_db_schema() {
    augur db create-schema

    echo
    echo "**********************************"
    echo "Schema created."
    echo "**********************************"
    echo
}


echo
echo "**********************************"
echo "Setting up database credentials..."
echo "**********************************"
echo

echo "Would you like to..."
install_locally="initialize a new database AND install the schema?"
install_remotely="connect to an existing empty database and ONLY install the schema?"
already_installed="connect to a database with the schema already installed?"

select install_location in "$install_locally" "$install_remotely" "$already_installed"
do
  case $install_location in
    $install_locally )
        echo "Please enter the credentials for the default (or maintenance) user for your instance."
        echo "These will be used to log in to the database so that Augur can initalize a new database and install the schema for you."

        read -p "Default DB name: " default_db_name
        read -p "Default user: " default_user
        read -p "Default user's password: " default_password

        echo
        echo "Please enter the host on which your instance is running, and the port it is listening on."
        read -p "Host: " host
        read -p "Port: " port
        echo

        echo
        echo "Now, please choose the credentials for the database you would create."
        echo "If you are not sure to put , we recommend naming both your database and user as augur."
        echo "The choice of password if up to you; just make sure you don't forget it."
        echo
        set_db_credentials true

        augur db init-database \
        --default-db-name $default_db_name \
        --default-user $default_user \
        --default-password $default_password \
        --target-db-name $db_name \
        --target-user $db_user \
        --target-password $password \
        --host $host \
        --port $port

        create_db_schema
        echo "DB created."
        break
      ;;
    $install_remotely )
        echo "Please enter the credentials for the database."
        set_db_credentials
        # https://www.youtube.com/watch?v=rs9wuaVV33I
        create_db_schema
        break
      ;;
    $already_installed )
        echo "Please enter the credentials for the database you have created."
        set_db_credentials
        break
      ;;
  esac
done



