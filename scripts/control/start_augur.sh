#!/bin/bash

echo "Starting backend server..."
nohup augur backend start > /dev/null 2>&1 &
