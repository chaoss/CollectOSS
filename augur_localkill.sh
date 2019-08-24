#!/bin/bash

# ./augurkill.sh
if [[ $(ps x -o pid= -p $(cat logs/augur_backend_pid.txt) | wc -l) -eq 1 ]]; then
    echo "Killing backend server."
    kill -9 $(cat logs/augur_backend_pid.txt)
else
    echo "Backend server was not running."
fi


# account for grep process itself here
# TODO: make this use pgrep/something more robust
if [[ $(ps ax | grep 'vue-cli-service serve' | awk '{print $1}' | wc -l) -eq 2 ]]; then
    echo "Killing frontend server."

    # because grep sees itself running, it will print an error message that there is no such process 
    # because by the time kill gets to it, grep is finished executing.
    # TODO: make this use pgrep/something more robust
    kill $(ps ax | grep 'vue-cli-service serve' | awk '{print $1}')
else
    echo "Frontend server was not running."
fi