#!/bin/bash

#automate the small things for setting up docker containers
touch docker_env.txt
#Prompt for user info
echo "Please input Github API key: "
read githubAPIKey

echo "AUGUR_GITHUB_API_KEY=$githubAPIKey" >> docker_env.txt

echo "Please choose which database hostname to use."
echo "Note: localhost will attempt to connect to a local database on your machine"
echo "0.0.0.0 will attempt to connect to a local database in a docker image on your machine"
echo "Any other hostname will work normally."
echo "Plase input database hostname: "
read dbHostname

echo "AUGUR_DB_HOST=$dbHostname" >> docker_env.txt
echo "AUGUR_DB_NAME=augur" >> docker_env.txt
echo "AUGUR_DB_PORT=5432" >> docker_env.txt
echo "AUGUR_DB_USER=augur" >> docker_env.txt
echo "AUGUR_DB_PASSWORD=augur" >> docker_env.txtrm 

docker-compose -f docker-compose.yml up