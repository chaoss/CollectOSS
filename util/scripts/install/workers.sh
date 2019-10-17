#!/bin/bash

echo
echo "**********************************"
echo "Installing workers and their dependencies..."
echo "**********************************"
echo

for WORKER in $(ls -d workers/*/)
do
    if [[ $WORKER == *"_worker"* ]]; then

      # make it pretty for formatting
      FORMATTED_WORKER=${WORKER/#workers\//}
      FORMATTED_WORKER=${FORMATTED_WORKER/%\//}

      echo
      echo "**********************************"
      echo "Installing $(basename $(pwd))..."
      echo "**********************************"
      echo

      cd $WORKER
      rm -rf build/*;
      rm -rf dist/*;
      python setup.py install;
      pip install -e .
      cd ../..
      echo "Installing $FORMATTED_WORKER"

    fi
done
