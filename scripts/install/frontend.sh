#!/bin/bash
set -euo pipefail

read -r -p "Would you like to install Augur's frontend dependencies? [Y/n] " response
case "$response" in
  [yY][eE][sS]|[yY]) 
    install_deps > logs/install/frontend.log 2>&1
    ;;
  *)
    echo "Skipping frontend dependencies..."
    ;;
esac

function install_deps() {

    if [[ $(command -V npm) ]]; then
    cd frontend/;
    echo "Installing frontend dependencies..."
    echo "**********************************"
    echo
    npm install brunch canvas vega @vue/cli;
    npm install; 
    npm run build;
    cd ../;
    echo "Done!"
    else
    echo
    echo "** npm not found. Please install NPM by either installing node (https://nodejs.org/en/download/) or by installing NPM itself."
    echo
    exit 1
    fi
}
