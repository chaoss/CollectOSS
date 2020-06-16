#!/bin/bash

echo "Removing Python caches..."
find . -name \*.__pycache__ -delete
find . -name \*.pytest_cache -delete
find . -name \*.pyc -delete

echo "Cleaning log files..."
find . -name \*.out -delete
find . -name \*.log -delete
find . -type f -name "*.lock" -delete