#!/bin/bash

echo "Removing node_modules, logs, caches, and some other dumb stuff that can be annoying..."
rm -rf frontend/public .pytest_cache logs *.out env.txt pyenv.txt
rm -rf workers/**/*.log workers/**/*.err workers/**/*.out
find . -name \*.pyc -delete
find . -type f -name "*.lock" -delete