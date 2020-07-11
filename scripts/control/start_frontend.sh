#!/bin/bash

if [[ ! -d logs ]]; then
    mkdir logs
fi

echo "Starting frontend server..."
cd frontend
nohup npm run serve > "../logs/frontend.log" 2>&1 &
cd ..
