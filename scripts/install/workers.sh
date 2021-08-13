#!/bin/bash
set -eo pipefail

echo "Installing workers and their dependencies..."
echo "**********************************"
echo

target=$1

for WORKER in $(ls -d workers/*/)
do
    if [[ $WORKER == *"_worker"* ]]; then

      if [[ \
        $WORKER != *"spdx_worker"* \
     && $WORKER != *"template_worker"* \
     && $WORKER != *"metric_status_worker"* \
     ]]; then

        # make it pretty for formatting
        FORMATTED_WORKER=${WORKER/#workers\//}
        FORMATTED_WORKER=${FORMATTED_WORKER/%\//}

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
        cd ../..
      fi

    fi


done

export PATH=$PATH:/usr/local/go/bin

if [ -d "$HOME/scorecard" ]; then
  echo " Scorecard already exists, skipping cloning ..."
else
  echo "Cloning OSSF Scorecard to generate scorecard data ..."
  git clone https://github.com/ossf/scorecard $HOME/scorecard
  CURRENT_DIR=$PWD;
  cd $HOME/scorecard;
  go build;
  echo "scorecard build done"
  cd $CURRENT_DIR
fi
