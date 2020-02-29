#!/bin/bash
set -euo pipefail

if [[ "$VIRTUAL_ENV" ]]; then
    echo "Killing augur processes..."
     ps aux | grep -ie $VIRTUAL_ENV/ |   awk '{print "kill -9 " $2}'
     ps -ef | grep -ie $VIRTUAL_ENV/ | grep -v grep | awk '{print $2}' | xargs kill

    echo "Killing worker processes..."
     ps aux | grep -ie $VIRTUAL_ENV/ | grep -ie bin | grep worker  |  awk '{print "kill -9 " $2}'
     ps -ef | grep -ie $VIRTUAL_ENV/ | grep -v grep | awk '{print $2}' | xargs kill
else
    echo "We noticed you're not in a virtual environment. Please activate your augur virtual environment and run the command again."
fi
