#!/bin/bash

if [[ "$VIRTUAL_ENV" ]]; then
    echo "Listing augur processes..."
     ps -efx | grep -ie $VIRTUAL_ENV/ | grep -v grep | awk '{print "PID " $2 ": " $8}'

    echo "Listing worker processes..."
     ps -efx | grep -ie $VIRTUAL_ENV/ | grep -v grep | grep worker | awk '{print "PID " $2 ": " $8}'
else
    echo "We noticed you're not in a virtual environment. Please activate your augur virtual environment and run the command again."
fi

