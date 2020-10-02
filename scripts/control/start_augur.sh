#!/bin/bash

echo "Starting backend server..."
nohup augur server start > /dev/null 2>&1 &
