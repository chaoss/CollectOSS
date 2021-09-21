#!/bin/bash

if [[ -z "$VIRTUAL_ENV" ]]; then
  echo "*** We noticed you're not currently inside a virtual environment. Augur MUST be run inside a virtual environment. ***"
  read -r -p "*** Would you like us to generate a environment for you automatically? If you select no, you must create it yourself. [Y/n] " response
  case "$response" in
      [yY][eE][sS]|[yY])
          echo
          $augur_python_command -m venv $HOME/.virtualenvs/augur_env
          echo "*** Your environment was installed to $HOME/.virtualenvs/augur_env/. Please activate your environment using your shell's appropriate command. ***"
          echo "*** For example, if you're using bash, run 'source $HOME/.virtualenvs/augur_env/bin/activate'. ***"
          echo "*** Once you've activated your virtual environment, please rerun the installation command. ***"
          exit 1
          ;;
      *)
          echo
          echo "Please create & activate your virtual environment and rerun the installation command when you're finished."
          exit 1
          ;;
  esac
fi

function check_python_version() {
  major_python_version=$($1 -c 'import sys; print(sys.version_info.major)')
  minor_python_version=$($1 -c 'import sys; print(sys.version_info.minor)')

  if [[ $major_python_version -lt 3 ]]; then
    echo "Outdated major version of Python detected."
    return 1
  elif [[ $minor_python_version -lt 6 ]]; then
    echo "Outdated minor version of Python detected."
    return 1
  fi
}

check_python_version "python"
if [[ $? -eq 1 ]]; then
  echo "Insufficient Python version installed to `which python`."
  echo "Checking `which python3`..."
  check_python_version "python3"
  if [[ $? -eq 1 ]]; then
    echo "Insufficient Python version installed to `which python3`."
    echo "Please install Python 3.6 or higher to either python or python3."
    echo "Python 3.6 and higher can be found here: https://www.python.org/downloads/"
    exit 1
  fi
fi

if [[ ! $(command -v pip) ]]; then
  echo "pip not found searching. Searching for pip3..."
  if [[ ! $(command -v pip3) ]]; then
    echo "Neither pip nor pip3 has been detected. Please make sure one of these two commands is installed and available in your PATH."
    echo "Installation instructions can be found here: https://pip.pypa.io/en/stable/installing/"
    exit 1
  fi
fi

if [[ ! -d logs ]]; then
    mkdir logs
fi

command -v go >/dev/null 2>&1 || { echo >&2 "We require 'go' to run Scorecard project to get data, Please install GO first....Aborting. Please issue the command: wget -c https://dl.google.com/go/go1.16.2.linux-amd64.tar.gz -O - | sudo tar -xz -C /usr/local "; exit 1; }