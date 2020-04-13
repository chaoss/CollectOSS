#!/bin/bash

if [[ ! -d logs ]]; then
    mkdir logs
fi

echo "Starting backend server..."
nohup augur run > logs/augur.log 2>&1 &
