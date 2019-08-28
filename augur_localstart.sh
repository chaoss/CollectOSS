#!/bin/bash

./augur_localkill.sh

if [[ $(ps x -o pid= -p $(cat logs/augur_backend_pid.txt) | wc -l) -ge 1 ]]; then
    echo "Backend server already running."
else
    echo "Starting backend server."
    nohup augur run > logs/augur_backend.log 2>&1 &
    echo $! > logs/augur_backend_pid.txt
fi

# account for grep process itself here
# TODO: make this use pgrep/something more robust
if [[ $(ps ax | grep 'vue-cli-service serve' | wc -l) -ge 2 ]]; then
    echo "Frontend server already running."
else
    echo "Starting frontend server."
    cd frontend/
    nohup npm run serve > ../logs/augur_frontend.log 2>&1 &
    echo $! > ../logs/augur_frontend_pid.txt
fi


