#!/bin/bash

rm -rf frontend/public .pytest_cache logs/**/*.log *.out env.txt pyenv.txt workers/**/*.log *.log
find . -name \*.pyc -delete
find . -type f -name "*.lock" -delete