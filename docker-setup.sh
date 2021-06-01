#!/bin/bash
if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

#automate the small things for setting up docker containers
#This file sets up the backend and the frontend and assumes the database is not in a container (which isn't recommended regardless)
rm docker_env.txt
touch docker_env.txt
#Prompt for user info
#TODO: Make container work with gitlab key
echo "Please input Github API key: "
read githubAPIKey

echo "AUGUR_GITHUB_API_KEY=$githubAPIKey" >> docker_env.txt

printf "\nPlease choose which database hostname to use."
echo "Plase input database hostname: "
read dbHostname

echo "AUGUR_DB_HOST=$dbHostname" >> docker_env.txt
echo "AUGUR_DB_NAME=augur" >> docker_env.txt
echo "AUGUR_DB_PORT=5432" >> docker_env.txt
echo "AUGUR_DB_USER=augur" >> docker_env.txt
echo "AUGUR_DB_PASSWORD=password" >> docker_env.txt

echo "Tearing down old docker stack..."
docker-compose -f docker-compose.yml down

echo "Starting set up of docker stack..."
docker-compose -f docker-compose.yml up

printf "\nNow showing active docker containers:\n"
docker container ls
printf "\n"

success=1
if [[ ! $(docker container ls | grep frontend) ]]; then
    echo "The frontend container failed to be deployed!"
    success=0
fi

if [[ ! $(docker container ls | grep backend) ]]; then
    echo "The backend container failed to be deployed!"
    success=0
fi


#Ask if the user wants to try again if either of the containers failed.
if [ $success -eq 0 ] ; then
  echo "Augur docker stack failed to be successfully deployed!"
  read -p "Would you like to try to deploy again? (y/n)" -n 1 -r
  echo

  #Be absolutely sure that the script gets a complete path to itself for restarting the process
  SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
  if [[ $REPLY =~ ^[Yy]$ ]]
  then
    exec "${SCRIPTPATH}/docker-setup.sh"
  else
    echo "Cleaning up failed deployment..."
    docker-compose -f docker-compose.yml down
  fi

  exit
fi

echo "Augur stack successfully deployed!"
