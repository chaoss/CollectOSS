#!/bin/bash

if [[ "$VIRTUAL_ENV" ]]; then
    echo "Listing augur processes..."
     ps -ef | grep -ie $VIRTUAL_ENV/ | grep -v grep | awk '{print $2}'

    echo "Listing worker processes..."
     ps aux | grep -ie $VIRTUAL_ENV/ | grep -ie bin | grep worker | awk '{print $2}'
else
    echo "We noticed you're not in a virtual environment. Please activate your augur virtual environment and run the command again."
fi

