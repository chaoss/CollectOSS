#!/bin/bash

# TODO: Packages for more OSes
PACKAGE_MANAGER="sudo apt-get -y install"
MYSQL_PACKAGE="mysql-server"
NODE_PACKAGE="nodejs"
GIT_PACKAGE="git"
CURL_PACKAGE="curl"
UNZIP_PACKAGE="unzip"
PYTHON_DEV="python-dev"
PYTHON_PACKAGE="python python-pip $PYTHON_DEV"
INSTALL_ANACONDA=0
HAS_ANACONDA=0
INSTALL_NODE_PPA=0
DEPENDENCY_INSTALL_COMMAND="$PACKAGE_MANAGER"
SCRIPT_DEPENDENCY_INSTALL_COMMAND="$PACKAGE_MANAGER"

function yes_or_no {
    read -p "$1 [y/n]: " -n 1 -r
  if [[ ! $REPLY =~ ^[Yy]$ ]]
  then
    printf "$2\n"
    return 1
  fi
  echo
  return 0
}

function yes_or_no_critical {
  if yes_or_no "$1" "$2"
  then
    return 0
  else
    [[ "$0" = "$BASH_SOURCE" ]] && exit 1 || return 1
  fi
}




#
# Dependencies
#
echo "Checking dependencies..."
echo "+-------------+----------+" 
echo "| Dependency  |  Status  |"
echo "+-------------+----------+" 

if hash mysql 2>/dev/null; then
  echo "| MySQL       |    found |"
else
  echo "| MySQL       |  missing |"
  DEPENDENCY_INSTALL_COMMAND+=" $MYSQL_PACKAGE"
fi

if hash node 2>/dev/null; then
  # TODO: Check node version
  echo "| Node        |    found |"
else
  echo "| Node        |  missing |"
  DEPENDENCY_INSTALL_COMMAND+=" $NODE_PACKAGE"
  INSTALL_NODE_PPA=1
fi

if hash pip 2>/dev/null; then
  echo "| Python      |    found |"
else
  echo "| Python      |  missing |"
  DEPENDENCY_INSTALL_COMMAND+=" $PYTHON_PACKAGE"
fi

if hash conda 2>/dev/null; then
  echo "| Anaconda    |    found |"
  HAS_ANACONDA=1
else
  echo "| Anaconda    |  missing |"
  INSTALL_ANACONDA=1
fi

if hash curl 2>/dev/null; then
  echo "| git         |    found |"
else
  echo "| git         |  missing |"
  SCRIPT_DEPENDENCY_INSTALL_COMMAND+=" $GIT_PACKAGE"
fi

if hash curl 2>/dev/null; then
  echo "| cURL        |    found |"
else
  echo "| cURL        |  missing |"
  SCRIPT_DEPENDENCY_INSTALL_COMMAND+=" $CURL_PACKAGE"
fi

echo "+-------------+----------+"

# Install dependencies for the installer to work
if [[ "$PACKAGE_MANAGER" != "$SCRIPT_DEPENDENCY_INSTALL_COMMAND"  ]]
then
  echo "This installation requires some additional packages to continue."
  if yes_or_no_critical "$SCRIPT_DEPENDENCY_INSTALL_COMMAND" "Installation aborted."
  then
      $SCRIPT_DEPENDENCY_INSTALL_COMMAND
  fi
fi

# Install NodeSource
if [[ "$INSTALL_NODE_PPA" == "1" ]]
then
  echo "Node is missing or out of date."
  if yes_or_no "Add NodeSource PPA (requires root priviledges)?" "NodeSource PPA skipped. Distribution node versions may not be compatible with Augur development."
  then
    curl -sL https://deb.nodesource.com/setup_7.x | sudo -E bash -
  fi
fi

# Install Anaconda
if [[ "$INSTALL_ANACONDA" == "1"  ]]
then
  printf "It is highly recommended to install Anaconda. Augur uses many packages included with Anaconda as well as Conda virtual environments.\nNot installing Anaconda may require sudo pip, which can potentially break system Python."
  if yes_or_no "Install Miniconda (34MB)?" "Anaconda not installed. Installation will use global Python environment."
  then
      curl -LOk https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
      chmod +x Miniconda3-latest-Linux-x86_64.sh
      ./Miniconda3-latest-Linux-x86_64.sh -b -p ~/.anaconda
      printf "# Added by Augur install script\nexport PATH=\"$HOME/.anaconda/bin:$PATH\"\n" >> ~/.bashrc
      printf "# Added by Augur install script\nexport PATH=\"$HOME/.anaconda/bin:$PATH\"\n" >> ~/.zshrc
      export PATH="$HOME/.anaconda/bin:$PATH"
      rm Miniconda3-latest-Linux-x86_64.sh
      echo "Anaconda installed to ~/.anaconda"
      conda install -c conda conda-env
      HAS_ANACONDA=1
  else
    INCLUDE_PY=$(python -c "from distutils import sysconfig as s; print s.get_config_vars()['INCLUDEPY']")
    if [ ! -f "${INCLUDE_PY}/Python.h" ]; then
      echo "Python development files are missing." >&2
      if yes_or_no_critical "$PACKAGE_MANAGER $PYTHON_DEV" "Installation aborted."
      then
        $PACKAGE_MANAGER $PYTHON_DEV
      fi
    fi
  fi
fi

# Install missing dependencies
if [[ "$PACKAGE_MANAGER" != "$DEPENDENCY_INSTALL_COMMAND" ]]
then
  if yes_or_no "$DEPENDENCY_INSTALL_COMMAND" "Dependencies not installed. Installation will likely fail."
  then
    $DEPENDENCY_INSTALL_COMMAND
  fi
fi



echo "All dependencies in place."


#
# Augur
#
echo 
echo "Downloading Augur..."
git clone https://github.com/OSSHealth/augur
cd augur
read -p "Would you like to install [m]aster or [d]ev: " -n 1 -r
DEVELOPER=0
if [[ $REPLY =~ ^[Dd]$ ]]
then
  DEVELOPER=1
  git checkout dev
fi

if hash conda 2>/dev/null; then
  echo "Creating conda environment..."
  conda env create -f environment.yml
  source activate augur
fi

pip install --upgrade .

if [[ $? != 0 ]]
then
  echo "Pip failed to install Augur. Some systems require root priviledges."
  yes_or_no_critical "Try again with sudo?" "Installation failed."
  sudo pip install --upgrade .
  if [[ $? != 0 ]]
  then
    echo "Installation failed."
    [[ "$0" = "$BASH_SOURCE" ]] && exit 1 || return 1
  fi
fi

echo "Augur Python application installed."




#
# Database
#
echo "Now we're going to set up the database. We'll need MySQL root credentials to proceed."

if yes_or_no "Continue with database setup?" "Database setup skipped. To manually set up database, augur and a default augur.cfg file will be created. Edit that file with the correct database settings.\nOr, run:\n\n curl -sOL https://raw.githubusercontent.com/OSSHealth/augur/dev/docs/install-msr.sh\nchmod +x install-msr.sh\n./install-msr.sh\n"
then
  ./docs/install-msr.sh
fi




#
# Node
#
echo "Installing brunch, apidoc, and yarn..."
npm install --global yarn apidoc brunch
if [[ $? != 0 ]]
then
  echo "NPM failed to install the packages. Some systems require root priviledges."
  yes_or_no_critical "Try again with sudo?" "Augur installed, but node install failed.\napidoc and brunch are required for development."
  sudo npm install --global yarn apidoc brunch
  if [[ $? != 0 ]]
  then
    echo "Installation failed."
    [[ "$0" = "$BASH_SOURCE" ]] && exit 1 || return 1
  fi
fi

echo "Installing Augur frontend node dependencies..."
cd frontend
yarn install
cd ../..

printf "\nInstall finished!\n\n"
if [[ "$HAS_ANACONDA" == "1" && "$INSTALL_ANACONDA" == "1" ]]
then
  echo "Anaconda will not be avalible without restarting your shell, or running 'source ~/.bashrc'"
fi
if [[ "$HAS_ANACONDA" == "1" ]]
then
  echo "You must activate the augur conda environment using 'source activate augur' before running augur."
fi
echo "To run augur, it must be run in the same directory as the augur.cfg file, or your settings must be provided as environment variables."
echo "The  folder contains a augur.cfg file generated for you during installalation."
echo "To run augur for development, cd into the project folder and run 'make dev-start' (requires GNU screen)"
if yes_or_no "Would you like to start Augur for development?" ""
then
  cd augur-*
  make dev-start
fi