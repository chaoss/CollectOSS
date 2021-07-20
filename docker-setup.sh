#!/bin/bash
#automate the small things for setting up docker containers
#This file sets up the backend and the frontend and optional database container.
#NOTE: The frontend is currently under construction.
#
#The script is needed to handle:
# -Environment variables for
#   -Runtime values needing to be set and accurate for the backend's database credentials and github api key
#   -Pre-runtime values needing to be set and accurate for the database hostname and type (whether it is test data or not). The ip address needs to be added in the extra_hosts argument of the yml markup.
# -Setting up a network alias in order to let the docker container communicate with local hosts.
# -Easily seeing console output and process statistics from one convienient window.
# -Easily save console output to logs.
#
#This file uses two environment files
# - One called docker_env.txt which holds the runtime enviroment variables that the container itself uses
# - One called .env which holds the environment variables that docker-compose.yml uses and holds the database type.
#TODO:
  #Let users know how to configure the database to work for local connection because its not *that* clear right now. Its in the docs at least.
  #Make container work with gitlab key
  #Test this script on macOS
#
missingModules=""

#Check everything that needs to be in the $PATH is in there.
#Bash doesn't let this work if this is in an if statement for some reason it has to be chained
type -P "docker" &>/dev/null && echo "docker found..." || missingModules="${missingModules} docker"
type -P "docker-compose" &>/dev/null && echo "docker-compose found..." || missingModules="${missingModules} docker-compose"
type -P "ifconfig" &>/dev/null && echo "ifconfig found..." || missingModules="${missingModules} ifconfig (part of net-tools)"
type -P "psql" &>/dev/null && echo "psql found..." || missingModules="${missingModules} psql"
type -P "watch" &>/dev/null && echo "watch found..." || missingModules="${missingModules} watch"

if [ ! -z "$missingModules" ]
then
  echo "One or more modules required to run this script is missing or not in your \$PATH:"
  echo "Note: OSX users will need to install watch with \"brew install watch\""
  echo "Including:$missingModules"
  exit 1
fi
unset $missingModules

if [ "$EUID" -ne 0 ];
  then echo "Please run as root"
  exit 1
fi

#Always use a clean .env file because it is a subset of docker_env.txt so we can just generate it from that.
if [[ -f ".env" ]]
then
  rm .env
fi
touch .env

#This is differant for MacOS
#Script uses an alias for localhost that is the below ip
echo "Setting up network alias..."
#Check kernel for OS, assumes either linux or macOS
if [ "$(uname -s)" == "Linux" ]
then
  ifconfig lo:0 10.254.254.254
  ifconfig lo:0
  echo "Linux detected..."
else
  ifconfig lo0 alias 10.254.254.254
  ifconfig lo0
fi

#Prompt for deploy type.
echo "Types of docker deployment: "
echo
echo "1. Deploy the backend using docker connected to a non-docker database."
echo "2. Deploy backend and database together in docker containers."
echo "3. Deploy the backend and database together in docker containers using premade test data."
echo
read -p "Would you like to use : " deployChoice

case $deployChoice in

  1)
    #Start script to set up just two containers
    exec scripts/docker/docker-setup-external.sh
    ;;
  
  2)
    #Start script to set up all three containers.
    #Set env variable to not use test data
    echo "AUGUR_DB_TYPE=database" >> .env
    exec scripts/docker/docker-setup-database.sh
    ;;

  3)
    #Start script to set up all three containers
    #Set env variable to use test data.
    echo "AUGUR_DB_TYPE=test_data" >> .env
    exec scripts/docker/docker-setup-database.sh
    ;;

  *)
    echo "Invalid choice!"
    exit 1
    ;;
esac
