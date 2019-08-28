#!/bin/bash
## Back End

PS3="Your choice: "

if [[ -z $VIRTUAL_ENV ]]; then
  echo "*** We noticed you're not using a virutal environment. It is STRONGLY recommended to install Augur in its own virutal environment. ***"
  echo "*** Would you like to create a virtual environment using virtualenv? ***"
  select choice in "Yes" "No"
  do
    case $choice in
      Yes )
          virtualenv -p python3.6 augur_venv
          echo "*** Your environment was installed as \`augur_venv\`. Please activate and restart the installation using your shell's appropriate command. ***"
          echo "*** For example, if you're using bash run 'source augur_venv/bin/activate'. ***"
          exit 0
        ;;
      No )
          echo "Resuming installation..."
          break
        ;;
    esac
  echo
done
fi

echo "Installing backend dependencies..."
rm -rf build/*; rm $VIRTUAL_ENV/bin/*worker*; 
pip install pipreqs sphinx; 
pip install -e .; pip install ipykernel; pip install xlsxwriter; python -m ipykernel install --user --name augur --display-name "Python (augur)"; 
python setup.py install;

echo "Installing workers and their dependencies..."
for OUTPUT in $(ls -d workers/*/)
do
    if [[ $OUTPUT == *"_worker"* ]]; then
        cd $OUTPUT
        echo "Running setup for $(basename $(pwd))"
        rm -rf build/*;
        rm -rf dist/*;
        python setup.py install;
        cd ../..
    fi
done

echo "Setting up the database configuration."

installpostgreslocally="Use a pre-existing Postgres 10 or 11 installation to which you can install the Augur schema?"
installpostgresremotely="Use a pre-existing Postgres 10 or 11 installation to which someone else can install the Augur schema?"
postgresalreadyinstalled="Use a pre-existing Postgres 10 or 11 installation with the Augur schema already installed? "
QUIT="Quit"

select haveinstalledpostgres in "$installpostgreslocally" "$installpostgresremotely" "$postgresalreadyinstalled" "$QUIT"
do
  case $haveinstalledpostgres in
      $QUIT )
      echo "Quitting..."
      break
    ;;
    $installpostgreslocally )
        echo "After you have installed the Augur schema to your database, please return to this point in the installation."
        echo "Please enter the credentials for your database."
        read -p "Host: " host
        read -p "name: " name
        read -p "password: " password
        read -p "port: " port
        read -p "schema: " schema
        read -p "Key: " key
        read -p "user: " user
      ;;
    $installpostgresremotely )
        echo "Once the Augur schema has been installed on to your database for you, please return to this point in the installation."
        echo "Please enter the credentials for your database."
        read -p "Host: " host
        read -p "name: " name
        read -p "password: " password
        read -p "port: " port
        read -p "schema: " schema
        read -p "Key: " key
        read -p "user: " user
        break
      ;;
    $postgresalreadyinstalled )
        echo "Please enter the credentials for your database."
        read -p "Database: " database
        read -p "Name: " name
        read -p "Host: " host
        read -p "Port: " port
        read -p "User: " user
        read -p "Password: " password
        read -p "Schema: " schema
        read -p "Key: " key
        read -p "Zombie ID: " zombie_id
        break
      ;;
  esac
done
echo

config="
{
  \"database\": \"$database\",
  \"name\": \"$name\",
  \"host\": \"$host\",
  \"port\": \"$port\",
  \"user\": \"$user\",
  \"password\": \"$password\",
  \"schema\": \"$schema\",
  \"key\": \"$key\",
  \"zombie_id\": \"$zombie_id\"
}"


rm temp.config.json
echo $config > temp.config.json

echo "Generating configuration file..."
python util/make-config.py

echo "Would you like to install Augur's frontend dependencies?"
select choice in Yes No
do
  case $choice in
    Yes )
      echo "Installing frontend dependencies..."
      cd frontend/;
      yarn install;
      yarn global add apidoc brunch newman @vue/cli; 
      yarn run build;
      cd ../;
      ;;
    No )
      echo "Skipping frontend dependencies..."
      ;;
  esac
echo "Setting up API documentation..."
cd docs && apidoc --debug -f "\.py" -i ../augur/ -o api/; rm -rf ../frontend/public/api_docs; mv api ../frontend/public/api_docs;
done
