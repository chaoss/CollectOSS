#!/bin/bash

echo "Starting backend server..."
nohup augur run > /dev/null 2>&1 &
