#!/bin/bash
if [ "$EUID" -ne 0 ];
  then echo "Please run as root"
  exit 1
fi

#automate the small things for setting up docker containers
#This file sets up the backend and the frontend and assumes the database is not in a container (which isn't recommended regardless)

#Always use a clean .env file because it is a subset of docker_env.txt so we can just generate it from that.
if [[ -f ".env" ]]
then
  rm .env
fi

touch .env
#Ask the user if they want to be prompted or use an existing config file (docker_env.txt)
read -p "Would you like to be prompted for database credentials? [y/N] " -n 1 -r
echo 

if [[ $REPLY =~ ^[Yy]$ ]]
then

  if [[ -f "docker_env.txt" ]]
  then
    rm docker_env.txt
  fi

  touch docker_env.txt

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
  if [ -z "$dbPassword" ]
  then
    dbPassword="password"
  fi

  echo "AUGUR_DB_PASSWORD=$dbPassword" >> docker_env.txt

else

  if [[ ! -f "docker_env.txt" ]]
  then
    echo "docker_env.txt not found. Please add environment variables in this file or restart the script and choose to prompt db credentials."
    exit 1
  fi

  #Copy host name to docker-compose env file.
  cat docker_env.txt | grep AUGUR_DB_HOST > .env
fi


echo "Tearing down old docker stack..."
docker-compose -f docker-compose.yml down


echo "Starting set up of docker stack..."
#Run docker stack in background to catch up to later
#This is done so that the script can check to see if the containers are sucessful while docker-compose is running.
docker-compose -f docker-compose.yml up --no-recreate & PIDOS=$!

#Wait until the docker containers should show up in a docker container ls call
sleep 5
printf "\nNow showing active docker containers:\n"
docker container ls
printf "\n"

#Check to see if full stack has been successfully deployed
success=1
if [[ ! $(docker container ls | grep frontend) ]]; then
    echo "The frontend container failed to be deployed!"
    success=0
fi

if [[ ! $(docker container ls | grep backend) ]]; then
    echo "The backend container failed to be deployed!"
    success=0
fi

#Wait for the user to kill docker-compose or for it to fail
wait $PIDOS
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

#Cleaning up dead containers
echo "Cleaning up dead containers... "
docker-compose -f docker-compose.yml down
echo "Augur stack successfully deployed!"
