#!/bin/bash

echo
echo "**********************************"
echo "Installing frontend dependencies..."
echo "**********************************"
echo

if [[ $(command -V npm) ]]; then
  cd frontend/;
  npm install brunch canvas vega @vue/cli;
  npm install; 
  npm run build;
  cd ../;
else
  echo
  echo "** npm not found. Please install NPM by either installing node (https://nodejs.org/en/download/) or by installing NPM itself."
  echo
  exit 1
fi