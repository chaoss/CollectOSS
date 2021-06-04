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

#This step isn't working properly idk why.
#docker-compose is acting very strangely and it seems to be starting 2 augur_backend containters at once?
#This makes no sense as it really just uses docker-comose.yml which doesn't tell it to make 2 containers.

#Needs to be something like
#docker run -i -t -p 5000:5000 --add-host=database:95.217.193.152  isaacmilarky/augur_backend 
#augur config init --db_name "augur_osshealth" --db_host "database" --db_port "5432" --db_user "augur" --db_password "covidparty" --github_api_key "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"
#but using docker compose

echo "Starting set up of docker stack..."
docker-compose -f docker-compose.yml up --no-recreate
#Try to write logs to a file
#docker-compose logs -f -t >> dockerIsBroken.log

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
