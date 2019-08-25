#!/bin/bash

echo "Augur processes:"
ps aux | grep -ie $VIRTUAL_ENV | grep -ie augur | awk '{print $2}'
kill $(ps aux | grep -ie $VIRTUAL_ENV | grep -ie augur | awk '{print $2}')
lsof -i tcp:5000

# echo "Worker processes" 
# ps aux | grep -ie $VIRTUAL_ENV | grep -ie bin | grep worker  | awk '{kill $2}'
