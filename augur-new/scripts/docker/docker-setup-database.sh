#This is where the scripts are differant.
githubAPIKey="dockerkey"

if [[ -f "docker_env.txt" ]]
then
    githubAPIKey=$(awk -F= -v key="AUGUR_GITHUB_API_KEY" '$1==key {print $2}' docker_env.txt)
    test -z "$githubAPIKey" && echo "No existing API key could be found!" || echo "Discovered existing api key $githubAPIKey"
    rm docker_env.txt
fi

touch docker_env.txt
echo "AUGUR_GITHUB_API_KEY=$githubAPIKey" >> docker_env.txt
echo "AUGUR_DB_SCHEMA_BUILD=0" >> docker_env.txt

dbHostname=10.254.254.254
#docker_env.txt is differant than '.env', '.env' is for the enviroment variables used in the docker-compose.yml file
echo "AUGUR_DB_HOST=$dbHostname" >> docker_env.txt
echo "AUGUR_DB_HOST=$dbHostname" >> .env
echo "AUGUR_DB_NAME=augur" >> docker_env.txt
echo "AUGUR_DB_PORT=5434" >> docker_env.txt
echo "AUGUR_DB_USER=augur" >> docker_env.txt
echo "AUGUR_DB_PASSWORD=augur" >> docker_env.txt

#This checks the .env file's environment variables NOT docker_env.txt.
#AUGUR_DB_TYPE is set by the parent script in the .env file.
dbType=$(awk -F= -v key="AUGUR_DB_TYPE" '$1==key {print $2}' .env)
#Handle test data.
if [ "$dbType" == "test_data" ]; then
  sed -i -r '/AUGUR_DB_NAME/ s/(^.*)(=.*)/\1=test_data/g' docker_env.txt
fi

#Ask the user if they want to be prompted or use an existing config file (docker_env.txt)
read -p "Would you like to be prompted for an api key? [y/N] " -n 1 -r
echo 
if [[ $REPLY =~ ^[Yy]$ ]]
then

  #Prompt for user info
  read -p "Please input Github API key: " githubAPIKey
  echo
  sed -i -r '/AUGUR_GITHUB_API_KEY/ s/(^.*)(=.*)/\1=1/g' docker_env.txt
fi


echo "Tearing down old docker stack..."
docker-compose -f docker-compose.yml -f database-compose.yml down --remove-orphans

#Run docker stack in background to catch up to later
echo "Starting set up of docker stack..."
nohup docker-compose -f docker-compose.yml -f database-compose.yml up --no-recreate &>/tmp/dockerComposeLog & 
PIDOS=$!

#While the containers are up show a watch monitor that shows container status and live feed from logs
printf "\nNow showing active docker containers:\n"
watch -n1 --color 'docker-compose -f docker-compose.yml -f database-compose.yml ps && echo && tail -n 30 /tmp/dockerComposeLog && echo "Ctrl+C to Exit"'
printf "\n"

#Stop the process and clean up dead containers on SIGINT.
kill -15 $PIDOS
#Cleaning up dead containers
echo "Cleaning up dead containers... "
docker-compose -f docker-compose.yml -f database-compose.yml down --remove-orphans
bash scripts/docker/cleanup.sh
