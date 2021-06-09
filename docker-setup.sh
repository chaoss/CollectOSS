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

#This is differant for MacOS
#Script uses an alias for localhost that is the below ip
echo "Setting up network alias..."
ifconfig lo:0 10.254.254.254
ifconfig lo:0

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

  if [ "$dbHostname" == "localhost" ]; then
    dbHostname=10.254.254.254
    echo "$dbHostname"
    echo "AUGUR_DB_SCHEMA_BUILD=1" >> docker_env.txt
    #Pass it to build argument in yml
    echo "AUGUR_DB_SCHEMA_BUILD=1" >> .env
  else
    echo "AUGUR_DB_SCHEMA_BUILD=0" >> docker_env.txt
    #Pass it to build argument in yml
    #echo "AUGUR_DB_SCHEMA_BUILD=0" >> .env
  fi


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
  cat docker_env.txt | grep AUGUR_DB_HOST >> .env
  #Copy build option for whether or not container builds a db schema
  #cat docker_env.txt | grep AUGUR_DB_SCHEMA_BUILD >> .env
fi

#Ask the user if they need augur to build schema or use an existing schema
#This is important because if it builds schema when it already exists it can cause probems.
#Its also important because if there is no schema augur throws an error (obviously).
read -p "Is there no existing schema on the database specified? [y/N] " -n 1 -r
echo 
if [[ $REPLY =~ ^[Yy]$ ]]
then
  #use some regex to set the schema build in docker_env.txt
  sed -i -r '/AUGUR_DB_SCHEMA_BUILD/ s/(^.*)(=.*)/\1=1/g' docker_env.txt
else
  sed -i -r '/AUGUR_DB_SCHEMA_BUILD/ s/(^.*)(=.*)/\1=0/g' docker_env.txt
fi

echo "Tearing down old docker stack..."
docker-compose -f docker-compose.yml down --remove-orphans

echo "Building images for deploy..."
docker-compose build

#Default value of 5 but you can input larger times if necessary.
read -p "Please input time in seconds to wait for containers to deploy [5 Seconds]: " timeout
timeout=${timeout:-5}
echo
echo "Starting set up of docker stack..."
#Run docker stack in background to catch up to later
#This is done so that the script can check to see if the containers are sucessful while docker-compose is running.
nohup docker-compose -f docker-compose.yml up --no-recreate &>/tmp/dockerComposeLog & 
PIDOS=$!

#Wait until the docker containers should show up in a docker container ls call
sleep $timeout

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

#Ask if the user wants to try again if either of the containers failed.
if [ $success -eq 0 ] ; then

  kill -9 $PIDOS
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
    docker-compose -f docker-compose.yml down --remove-orphans
  fi

  echo "Removing network interface..."
  ifconfig lo:0 down
  exit 1
fi


#While the containers are up show a watch monitor that shows container status and live feed from logs
printf "\nNow showing active docker containers:\n"
watch -n1 --color 'docker-compose ps && echo && tail -n 30 /tmp/dockerComposeLog && echo "Ctrl+C to Exit"'
printf "\n"


#Stop the process and clean up dead containers on SIGINT.
kill -15 $PIDOS
#Cleaning up dead containers
echo "Cleaning up dead containers... "
docker-compose -f docker-compose.yml down --remove-orphans

echo "Removing network interface..."
ifconfig lo:0 down

#Ask user if they would like to store logs to a permanent file.
#Might want to make where the logs are saved a constant. Right now it just dumps it in the current directory.
read -p "Would you like to store container output in a log file? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
  #uses . as the delimiter in order to ignore file extension inputted by user.
  read -p "Please input log filename: " logFileName
  #Deal with empty user input
  logFileName=${logFileName:-docker}
  #Get input up until .
  echo "Logs written to file: "
  echo "$(echo $logFileName | grep -E "^([^.]+)").log"

  cat /tmp/dockerComposeLog > "$(echo $logFileName | grep -E "^([^.]+)").log"
  rm /tmp/dockerComposeLog
else
  rm /tmp/dockerComposeLog
fi