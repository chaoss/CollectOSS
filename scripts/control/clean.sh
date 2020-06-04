#!/bin/bash

rm -rf frontend/public .pytest_cache logs/* *.out env.txt pyenv.txt
find . -name \*.pyc -delete
find . -type f -name "*.lock" -delete