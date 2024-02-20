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

if [ -f "/usr/local/go/bin/go" ] || [ -f "/usr/local/bin/go" ] || [ -f "/usr/bin/go" ] || [ -f "/snap/bin/go" ] || [ -f "/opt/homebrew/bin/go" ]; then
  echo "found go!"
else
  echo "Installing go!"
  curl -fsSLo- https://s.id/golang-linux | bash
  export GOROOT="/home/$USER/go"
  export GOPATH="/home/$USER/go/packages"
  export PATH=$PATH:$GOROOT/bin:$GOPATH/bin
fi

if [ -d "$HOME/scorecard" ]; then
  echo " Scorecard already exists, skipping cloning ..."
  echo " Updating Scorecard ... "
  #rm -rf $HOME/scorecard 
  #echo "Cloning OSSF Scorecard to generate scorecard data ..."
  #git clone https://github.com/ossf/scorecard $HOME/scorecard
  #cd $HOME/scorecard
  CURRENT_DIR=$PWD;
  cd $CURRENT_DIR
  cd $HOME/scorecard;
  #go build;
  #echo "scorecard build done"
  #cd $CURRENT_DIR
  #CURRENT_DIR=$PWD;
  #cd $HOME/scorecard; 
  git pull;
  go mod tidy; 
  go build; 
  echo "Scorecard build done."
  cd $CURRENT_DIR

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

#Do the same thing for scc for value worker
if [ -d "$HOME/scc" ]; then
  echo " Scc already exists, skipping cloning ..."
  echo " Updating Scc ... "
  rm -rf $HOME/scc  
fi

echo "Cloning Sloc Cloc and Code (SCC) to generate value data ..."
git clone https://github.com/boyter/scc $HOME/scc
cd $HOME/scc
CURRENT_DIR=$PWD;
cd $CURRENT_DIR
cd $HOME/scc;
go build;
echo "scc build done"
cd $CURRENT_DIR
