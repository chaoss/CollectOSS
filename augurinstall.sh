#!/bin/bash
## Back End

PS3="Your choice: "

function check_python_version() {
  major_python_version=$($1 -c 'import sys; print(sys.version_info.major)')
  minor_python_version=$($1 -c 'import sys; print(sys.version_info.minor)')

  if [[ $major_python_version -lt 3 ]]; then
    echo "Outdated major version of Python detected."
    return 1
  elif [[ $minor_python_version -lt 6 ]]; then
    echo "Outdated minor version of Python detected."
    return 1
  fi
}

augur_python_command=""

check_python_version "python"
if [[ $? -eq 1 ]]; then
  echo "Insufficient Python version installed to `which python`."
  echo "Checking `which python3`..."
  check_python_version "python3"
  if [[ $? -eq 1 ]]; then
    echo "Insufficient Python version installed to `which python3`."
    echo "Please install Python 3.6 or higher to either python or python3."
    echo "Python 3.6 and higher can be found here: https://www.python.org/downloads/"
    exit 1
  else
    echo "Sufficient version of Python found under `which python3`. Resuming installation..."
    augur_python_command="python3"
  fi
else
  echo "Sufficient version of Python found under `which python`. Resuming installation..."
  augur_python_command="python"
fi

if [[ ! $(command -v pip) ]]; then
  echo "pip not found searching. Searching for pip3..."
  if [[ ! $(command -v pip3) ]]; then
    echo "Neither pip nor pip3 has been detected. Please make sure one of these two commands is installed and available in your PATH."
    echo "Installation instructions can be found here: https://pip.pypa.io/en/stable/installing/"
    exit 1
  fi
echo "Some form of pip detected. Resuming installation..."
fi

if [[ -z $VIRTUAL_ENV ]]; then
  echo "*** We noticed you're not using a virutal environment. It is STRONGLY recommended to install Augur in its own virutal environment. ***"
  echo "*** Would you like to create a virtual environment? ***"
  select choice in "Yes" "No"
  do
    case $choice in
      Yes )
          echo "Would you like to generate the environment automatically, or configure it yourself?"
          echo "If you choose to create it automatically, virtualenv will be installed if it isn't already."
          select choice in "Yes" "No"
          do
            case $choice in
              "Yes" )
                  pip install virtualenv
                  virtualenv -p $augur_python_command augur_venv
                  echo "*** Your environment was installed as \`augur_venv\`. Please activate and restart the installation using your shell's appropriate command. ***"
                  echo "*** For example, if you're using bash run 'source augur_venv/bin/activate'. ***"
                  exit 0
                ;;
              "No" )
                  echo "Please create the virtual environment and return to the installation when you're finished."
                  exit 0
                ;;
            esac
          done
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
echo "If you need to install Postgres, the downloads can be found here: https://www.postgresql.org/download/"

installpostgreslocally="Would you like to use a pre-existing Postgres 10 or 11 installation to which you can install the Augur schema?"
installpostgresremotely="Would you like to use a pre-existing Postgres 10 or 11 installation to which someone else can install the Augur schema?"
postgresalreadyinstalled="Would you like to use a pre-existing Postgres 10 or 11 installation with the Augur schema already installed? "
SKIP="Skip this section"

select haveinstalledpostgres in "$installpostgreslocally" "$installpostgresremotely" "$postgresalreadyinstalled" "$SKIP"
do
  case $haveinstalledpostgres in
      $SKIP )
      echo "Skipping database configuration..."
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
      npm install;
      npm add apidoc brunch @vue/cli; 
      npm run build;
      cd ../;
      break
      ;;
    No )
      echo "Skipping frontend dependencies..."
      break
      ;;
  esac
echo "Setting up API documentation..."
cd docs && apidoc --debug -f "\.py" -i ../augur/ -o api/; rm -rf ../frontend/public/api_docs; mv api ../frontend/public/api_docs;
done


echo "*** INSTALLATION COMPLETE ***"
