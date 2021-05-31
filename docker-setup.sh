#!/bin/bash
if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

#automate the small things for setting up docker containers
rm docker_env.txt
touch docker_env.txt
#Prompt for user info
#TODO: Make container work with gitlab key
echo "Please input Github API key: "
read githubAPIKey

echo "AUGUR_GITHUB_API_KEY=$githubAPIKey" >> docker_env.txt

echo "Please choose which database hostname to use."
echo "Plase input database hostname: "
read dbHostname

echo "AUGUR_DB_HOST=$dbHostname" >> docker_env.txt
echo "AUGUR_DB_NAME=augur" >> docker_env.txt
echo "AUGUR_DB_PORT=5432" >> docker_env.txt
echo "AUGUR_DB_USER=augur" >> docker_env.txt
echo "AUGUR_DB_PASSWORD=password" >> docker_env.txt

docker-compose -f docker-compose.yml up