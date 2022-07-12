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


function create_config(){
    get_api_key_and_repo_path

    cmd=( augur config init --github_api_key $github_api_key --gitlab_api_key $gitlab_api_key --facade_repo_directory $facade_repo_directory )

    "${cmd[@]}" 
}

function config_prompt() {
    read -r -p "Would you like to generate a new config? [Y/n] " response
      case "$response" in
          ([yY][eE][sS]|[yY])
              echo "Generating default config..."
              create_config
              echo "Default config loaded"
              ;;
          *)
              ;;
      esac
}

config_prompt




