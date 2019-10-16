#!/bin/bash

echo
echo "**********************************"
echo "Setting up documentation..."
echo "**********************************"
echo

cd docs && apidoc -f "\.py" -i ../augur/ -o api/; rm -rf ../frontend/public/api_docs; mv api ../frontend/public/api_docs; cd ..

