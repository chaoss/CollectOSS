#!/bin/bash

util/scripts/install/checks.sh

if [[ $? -ne 0 ]]; then
  exit 1
fi

#remove annoying stuff
rm -rf runtime node_modules frontend/node_modules frontend/public augur.egg-info .pytest_cache logs 
find . -name \*.pyc -delete

#remove build files
rm -rf build/ dist/ docs/build/ workers/**/build/** workers/**/dist**

#rebuild everything
util/scripts/install/backend.sh
util/scripts/install/workers.sh
util/scripts/install/docs.sh
util/scripts/install/frontend.sh