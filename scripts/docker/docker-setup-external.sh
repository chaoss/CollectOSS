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
  read -p "Please input Github API key: " githubAPIKey
  echo "AUGUR_GITHUB_API_KEY=$githubAPIKey" >> docker_env.txt
  echo

  echo "Please choose which database hostname to use in the form of an ip or \'localhost\'"
  read -p "Plase input database hostname: " dbHostname

  #Do a quick translate from 'localhost' to the network alias on lo:0
  if [ "$dbHostname" == "localhost" ]; then
    dbHostname=10.254.254.254
    echo "$dbHostname"
    echo "AUGUR_DB_SCHEMA_BUILD=1" >> docker_env.txt
    #Pass it to build argument in yml
    echo "AUGUR_DB_SCHEMA_BUILD=1" >> .env
  else
    echo "AUGUR_DB_SCHEMA_BUILD=0" >> docker_env.txt
  fi

  #docker_env.txt is differant than '.env', '.env' is for the enviroment variables used in the docker-compose.yml file
  echo "AUGUR_DB_HOST=$dbHostname" >> docker_env.txt
  echo "AUGUR_DB_HOST=$dbHostname" >> .env

  #Pretty sure these stay constant among augur databases
  echo "AUGUR_DB_NAME=augur" >> docker_env.txt
  echo "AUGUR_DB_PORT=5432" >> docker_env.txt
  echo "AUGUR_DB_USER=augur" >> docker_env.txt

  #Password is blurred out because thats the standard
  read -s -p "Please input database password: " dbPassword
  echo

  #If blank, use default password 'password'
  if [ -z "$dbPassword" ]
  then
    dbPassword="password"
  fi
  echo "AUGUR_DB_PASSWORD=$dbPassword" >> docker_env.txt
else

  #docker_env.txt should always be present in a docker-compose build otherwise it can cause issues for the database.
  if [[ ! -f "docker_env.txt" ]]
  then
    echo "docker_env.txt not found. Please add environment variables in this file or restart the script and choose to prompt db credentials."
    exit 1
  fi

  #Copy host name to docker-compose env file.
  cat docker_env.txt | grep AUGUR_DB_HOST >> .env
fi

#Test the database connection
testHost=$(awk -F= -v key="AUGUR_DB_HOST" '$1==key {print $2}' docker_env.txt)
testPassword=$(awk -F= -v key="AUGUR_DB_PASSWORD" '$1==key {print $2}' docker_env.txt)
testName=$(awk -F= -v key="AUGUR_DB_NAME" '$1==key {print $2}' docker_env.txt)
testUser=$(awk -F= -v key="AUGUR_DB_USER" '$1==key {print $2}' docker_env.txt)

#Test connection using quick bash database request. $? now holds the exit code.
psql -d "postgresql://$testUser:$testPassword@$testHost/$testName" -c "select now()" &>/dev/null
if [[ ! "$?" -eq 0 ]]
then
  echo "Database could not be reached!"
  #This prompts the user because the *.conf files are in differant places on differant distros/OS's
  echo "Check pg_hba.conf and postgres.conf"
  exit 1
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

#Get images before final deploy
echo "Building images for deploy..."
docker-compose build
#Image has to be downloaded because current frontend is a WIP.
echo "Downloading frontend..."
docker-compose pull

#Run docker stack in background to catch up to later
#This is done so that the script can check to see if the containers are sucessful while docker-compose is running.
echo "Starting set up of docker stack..."
nohup docker-compose -f docker-compose.yml up --no-recreate &>/tmp/dockerComposeLog & 
PIDOS=$!

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
  read -p "Please input log filename: " logFileName
  #Deal with empty user input
  logFileName=${logFileName:-docker}
  
  #Get input up until .
  echo "Logs written to file: "
  echo "$(echo $logFileName | grep -E "^([^.]+)").log"

  #Save log to /var/log/ and delete the /tmp log.
  cat /tmp/dockerComposeLog > "/var/log/$(echo $logFileName | grep -E "^([^.]+)").log"
  echo "/var/log/$logFileName has been saved to disk."
  rm /tmp/dockerComposeLog
else
  rm /tmp/dockerComposeLog
fi

