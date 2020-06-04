#!/bin/bash

monitor=${1-quick}

if [[ $monitor == "quick" ]]; then

  echo "augur logs"
  echo "*****************************"
  tail -n 20 logs/augur.log

  for directory in `find logs/workers/ -type d`
  do
    echo
    echo $directory
    echo "*****************************"
    tail -n 20 $D/*_collection.log
    echo
  done

else
  less -F logs/augur.log logs/workers/**/*_collection.log
fi