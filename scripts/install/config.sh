#!/bin/bash

PS3="
Please type the number corresponding to your selection and then press the Enter/Return key.
Your choice: "

target=$1

function get_github_api_key(){
    echo
    echo "Please provide a valid GitHub API key."
    echo "For more information on how to create the key, visit:"
    echo "https://oss-augur.readthedocs.io/en/dev/getting-started/installation.html#backend"
    echo "** This is required for Augur to gather data ***"
    read -p "GitHub API Key: " github_api_key
    echo
}

function get_gitlab_api_key(){
    echo
    echo "Please provide a valid GitLab API key."
    echo "For more information on how to create the key, visit:"
    echo "https://oss-augur.readthedocs.io/en/dev/getting-started/installation.html#backend"
    echo "** This is required for Augur to gather data ***"
    read -p "GitLab API Key: " gitlab_api_key
    echo
}

function get_facade_repo_path() {

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


function create_config(){

    if [[ -z "${AUGUR_GITHUB_API_KEY}" ]]
    then
        get_github_api_key
    else
    echo
    echo "Found AUGUR_GITHUB_API_KEY environment variable with value $AUGUR_GITHUB_API_KEY"
    echo "Using it in the config" 
    echo "Please unset AUGUR_GITHUB_API_KEY if you would like to be prompted for a github api key"
      github_api_key=$AUGUR_GITHUB_API_KEY
    fi

    if [[ -z "${AUGUR_GITLAB_API_KEY}" ]]
    then
        get_gitlab_api_key
    else
    echo
    echo "Found AUGUR_GITLAB_API_KEY environment variable with value $AUGUR_GITLAB_API_KEY"
    echo "Using it in the config" 
    echo "Please unset AUGUR_GITLAB_API_KEY if you would like to be prompted for a gitlab api key"
      gitlab_api_key=$AUGUR_GITLAB_API_KEY
    fi

    if [[ -z "${AUGUR_FACADE_REPO_DIRECTORY}" ]]
    then
        get_facade_repo_path
    else
    echo
    echo "Found AUGUR_FACADE_REPO_DIRECTORY environment variable with value $AUGUR_FACADE_REPO_DIRECTORY"
    echo "Using it in the config" 
    echo "IMPORTANT NOTE: This assumes that this directory already exists"
    echo "Please unset AUGUR_FACADE_REPO_DIRECTORY if you would like to be prompted for the facade repo directory"
      facade_repo_directory=$AUGUR_FACADE_REPO_DIRECTORY
    fi
    
    cmd=( augur config init --github_api_key $github_api_key --gitlab_api_key $gitlab_api_key --facade_repo_directory $facade_repo_directory )

    "${cmd[@]}" 
}
echo
echo "Collecting data for config..."
create_config
echo
echo "Config created"
echo

# config_prompt




