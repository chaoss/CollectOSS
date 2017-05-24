#!/bin/bash

# TODO: Packages for more OSes
PACKAGE_MANAGER="sudo apt-get -y install"
MYSQL_PACKAGE="mysql-server"
NODE_PACKAGE="nodejs"
CURL_PACKAGE="curl"
UNZIP_PACKAGE="unzip"
INSTALL_ANACONDA=0
INSTALL_NODE_PPA=0
PYTHON_DEV="python-dev"
PYTHON_PACKAGE="python python-pip $PYTHON_DEV"
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
else
  echo "| Anaconda    |  missing |"
  INSTALL_ANACONDA=1
fi

if hash curl 2>/dev/null; then
  echo "| cURL        |    found |"
else
  echo "| cURL        |  missing |"
  SCRIPT_DEPENDENCY_INSTALL_COMMAND+=" $CURL_PACKAGE"
fi

if hash unzip 2>/dev/null; then
  echo "| unzip       |    found |"
else
  echo "| unzip       |  missing |"
  SCRIPT_DEPENDENCY_INSTALL_COMMAND+=" $UNZIP_PACKAGE"
fi

echo "+-------------+----------+"

# Install dependencies for the installer to work
if [[ "$PACKAGE_MANAGER" != "$SCRIPT_DEPENDENCY_INSTALL_COMMAND"  ]]
then
  echo "This installation requires curl and unzip to work."
  if yes_or_no_critical "$SCRIPT_DEPENDENCY_INSTALL_COMMAND" "Installation aborted."
  then
      $SCRIPT_DEPENDENCY_INSTALL_COMMAND
  fi
fi

# Install NodeSource
if [[ "$INSTALL_NODE_PPA" == "1" ]]
then
  echo "Node is missing or out of date."
  if yes_or_no "Add NodeSource PPA (requires root priviledges)?" "NodeSource PPA skipped. Distribution node versions may not be compatible with GHData development."
  then
    curl -sL https://deb.nodesource.com/setup_7.x | sudo -E bash -
  fi
fi

# Install Anaconda
if [[ "$INSTALL_ANACONDA" == "1"  ]]
then
  printf "It is highly recommended to install Anaconda. GHData uses many packages included with Anaconda as well as Conda virtual environments.\nNot installing Anaconda may require sudo pip, which can potentially break system Python."
  if yes_or_no "Install Miniconda (34MB)?" "Anaconda not installed. Installation will use global Python environment."
  then
      curl -LOk https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
      chmod +x Miniconda3-latest-Linux-x86_64.sh
      ./Miniconda3-latest-Linux-x86_64.sh -b -p ~/.anaconda
      printf "# Added by GHData install script\nexport PATH=\"$HOME/.anaconda/bin:$PATH\"\n" >> ~/.bashrc
      printf " Added by GHData install script\nexport PATH=\"$HOME/.anaconda/bin:$PATH\"\n" >> ~/.zshrc
      export PATH="$HOME/.anaconda/bin:$PATH"
      rm Miniconda3-latest-Linux-x86_64.sh
      echo "Anaconda installed to ~/.anaconda"
      conda install -c conda conda-env
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
# GHData
#
echo 
echo "Downloading GHData..."
read -p "Would you like to install [m]aster or [d]ev: " -n 1 -r
DEVELOPER=0

if [[ $REPLY =~ ^[Dd]$ ]]
then
  DEVELOPER=1
  curl -Lk https://github.com/OSSHealth/ghdata/archive/dev.zip > ghdata.zip
else
  curl -Lk https://github.com/OSSHealth/ghdata/archive/master.zip > ghdata.zip
fi

unzip ghdata.zip
cd ghdata-*
if hash conda 2>/dev/null; then
  echo "Creating conda environment..."
  conda env create -f environment.yml
  source activate ghdata
fi

pip install --upgrade .

if [[ $? != 0 ]]
then
  echo "Pip failed to install GHData. Some systems require root priviledges."
  yes_or_no_critical "Try again with sudo?" "Installation failed."
  sudo pip install --upgrade .
  if [[ $? != 0 ]]
  then
    echo "Installation failed."
    [[ "$0" = "$BASH_SOURCE" ]] && exit 1 || return 1
  fi
fi

echo "GHData Python application installed."




#
# Database
#
echo "Now we're going to set up the database. We'll need MySQL root credentials to proceed."

if yes_or_no "Continue with database setup?" "Database setup skipped. To manually set up database, ghdata and a default ghdata.cfg file will be created. Edit that file with the correct database settings.\nOr, run "
then
  curl -sL https://raw.githubusercontent.com/OSSHealth/ghdata/dev/docs/install-msrS.sh | bash -
fi




#
# Node
#
echo "Installing brunch, apidoc, and yarn..."
npm install --global yarn apidoc brunch
if [[ $? != 0 ]]
then
  echo "NPM failed to install the packages. Some systems require root priviledges."
  yes_or_no_critical "Try again with sudo?" "GHData installed, but node install failed.\napidoc and brunch are required for development."
  sudo npm install --global yarn apidoc brunch
  if [[ $? != 0 ]]
  then
    echo "Installation failed."
    [[ "$0" = "$BASH_SOURCE" ]] && exit 1 || return 1
  fi
fi

echo "Installing GHData frontend node dependencies..."
cd frontend
yarn install
cd ../..

printf "\nInstall finished!"