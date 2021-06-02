#!/bin/bash
if [ "$EUID" -ne 0 ];
  then echo "Please run as root"
  exit 1
fi

#automate the small things for setting up docker containers
#This file sets up the backend and the frontend and assumes the database is not in a container (which isn't recommended regardless)
rm docker_env.txt
rm .env
touch docker_env.txt
touch .env

#Prompt for user info
#TODO: Make container work with gitlab key
read -p "Please input Github API key: " githubAPIKey

echo "AUGUR_GITHUB_API_KEY=$githubAPIKey" >> docker_env.txt
echo
echo "Please choose which database hostname to use."
read -p "Plase input database hostname: " dbHostname

#docker_env.txt is differant than .env for some reason.
echo "AUGUR_DB_HOST=$dbHostname" >> docker_env.txt
echo "AUGUR_DB_HOST=$dbHostname" >> .env

echo "AUGUR_DB_NAME=augur" >> docker_env.txt
echo "AUGUR_DB_PORT=5432" >> docker_env.txt
echo "AUGUR_DB_USER=augur" >> docker_env.txt

read -p "Please input database password: " dbPassword

#If blank, use default password 'password'
if [ -z "$dbPassword"];
  then
  dbPassword="password"
fi

echo "AUGUR_DB_PASSWORD=$dbPassword" >> docker_env.txt

echo "Tearing down old docker stack..."
docker-compose -f docker-compose.yml down

#This step isn't working properly idk why.
#Needs to be something like
#augur config init --db_name "augur_osshealth" --db_host "database" --db_port "5432" --db_user "augur" --db_password "covidparty" --github_api_key "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"
#docker run -i -t -p 5000:5000 --add-host=database:95.217.193.152  isaacmilarky/augur_backend 
#but using docker compose

echo "Starting set up of docker stack..."
docker-compose -f docker-compose.yml --env-file docker_env.txt up

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
  read -p "Would you like to try to deploy again? [y/N] " -n 1 -r
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

  exit 1
fi

echo "Augur stack successfully deployed!"
