#!/bin/bash

if [[ "$VIRTUAL_ENV" ]]; then
    echo "Killing augur processes..."
     ps -efx | grep -ie $VIRTUAL_ENV/ | grep -v grep | awk '{print "Killing PID " $2 ": " $8 }'
     ps -efx | grep -ie $VIRTUAL_ENV/ | grep -v grep | awk '{print $2}' | xargs kill

    echo "Killing worker processes..."
     ps -efx | grep -ie $VIRTUAL_ENV/ | grep -v grep | grep worker | awk '{print "Killing PID " $2 ": " $8 }'
     ps -efx | grep -ie $VIRTUAL_ENV/ | grep -v grep | awk '{print $2}' | xargs kill
else
    echo "We noticed you're not in a virtual environment. Please activate your augur virtual environment and run the command again."
fi
