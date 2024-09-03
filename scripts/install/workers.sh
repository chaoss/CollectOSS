#!/bin/bash
set -eo pipefail

echo "Installing workers and their dependencies..."
echo "**********************************"
echo

target=$1

for WORKER in $(ls -d augur/tasks/data_analysis/*/)
do
    if [[ \
      $WORKER != *"spdx_worker"* \
   && $WORKER != *"template_worker"* \
   && $WORKER != *"metric_status_worker"* \
   && $WORKER != *"__pycache__"* \
   && $WORKER != *"contributor_breadth_worker"* \
   ]]; then

      # make it pretty for formatting
      FORMATTED_WORKER=$(basename $WORKER)

      echo
      echo "**********************************"
      echo "Installing $FORMATTED_WORKER..."
      echo "**********************************"
      echo

      cd $WORKER
      rm -rf build/*;
      rm -rf dist/*;
      if [[ $target == *"prod"* ]]; then
          pip install .
      else
          pip install -e .[dev]
      fi
      cd ../../../../
    fi

done

if [ -f "/usr/local/go/bin/go" ] || [ -f "/usr/local/bin/go" ] || [ -f "/usr/bin/go" ] || [ -f "/snap/bin/go" ]; then
  echo "found go!"
else
  echo "Installing go!"
  curl -fsSLo- https://s.id/golang-linux | bash
  export GOROOT="/home/$USER/go"
  export GOPATH="/home/$USER/go/packages"
  export PATH=$PATH:$GOROOT/bin:$GOPATH/bin
fi

SCORECARD_DIR="$HOME/scorecard"

# read -r -p "What directory would you like to use for OSSF Scorecard? [$HOME/scorecard] " response
# TODO: scorecard directory must be configurable

if [ -d "$SCORECARD_DIR" ]; then
  echo " Scorecard directory already exists, would you like to skip cloning and building?"
  echo " Only do this if Scorecard has been cloned and built in this directory before."
  read -r -p "If you choose NO (the default), Everything in $SCORECARD_DIR will be DELETED [y/N]: " response
  case "$response" in
    [yY][eE][sS]|[yY])
      echo " Skipping scorecard build"
      ;;
    *)
      echo " Cloning Scorecard ... "
      rm -rf $SCORECARD_DIR 
      echo "Cloning OSSF Scorecard to generate scorecard data ..."
      git clone https://github.com/ossf/scorecard $SCORECARD_DIR
      cd $SCORECARD_DIR
      CURRENT_DIR=$PWD;
      cd $CURRENT_DIR
      cd $SCORECARD_DIR;
      go build;
      echo "scorecard build done"
      cd $CURRENT_DIR
      ;;
  esac
else
  echo "Cloning OSSF Scorecard to generate scorecard data ..."
  git clone https://github.com/ossf/scorecard $SCORECARD_DIR
  cd $SCORECARD_DIR
  CURRENT_DIR=$PWD;
  cd $CURRENT_DIR
  cd $SCORECARD_DIR;
  go build;
  echo "scorecard build done"
  cd $CURRENT_DIR
fi
