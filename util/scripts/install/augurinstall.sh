#!/bin/bash

PS3="
Please type the number corresponding to your selection and then press the Enter/Return key.
Your choice: "

echo
echo "**********************************"
echo "Checking for python..."
echo "**********************************"
echo

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
    echo "Sufficient version of Python found at `which python3`. Resuming installation..."
    augur_python_command="python3"
  fi
else
  echo "Sufficient version of Python found at `which python`. Resuming installation..."
  augur_python_command="python"
fi

echo
echo "**********************************"
echo "Checking for pip..."
echo "**********************************"
echo
if [[ ! $(command -v pip) ]]; then
  echo "pip not found searching. Searching for pip3..."
  if [[ ! $(command -v pip3) ]]; then
    echo "Neither pip nor pip3 has been detected. Please make sure one of these two commands is installed and available in your PATH."
    echo "Installation instructions can be found here: https://pip.pypa.io/en/stable/installing/"
    exit 1
  else
    echo "Sufficient form of pip detected at `which pip3`. Resuming installation..."
  fi
else
  echo "Sufficient form of pip detected at `which pip`. Resuming installation..."
fi

echo
echo "**********************************"
echo "Checking for virtual environment..."
echo "**********************************"
echo
if [[ -z $VIRTUAL_ENV ]]; then
  echo "*** We noticed you're not using a virtual environment. It is STRONGLY recommended to install Augur in its own virtual environment. ***"
  echo "*** Would you like to create a virtual environment? ***"
  select choice in "Yes" "No"
  do
    case $choice in
      Yes )
          echo "Would you like to generate the environment automatically, or configure it yourself?"
          select choice in "Yes" "No"
          do
            case $choice in
              "Yes" )
                  echo
                  $augur_python_command -m venv $HOME/.virtualenvs/augur_env
                  echo "*** Your environment was installed to $HOME/.virtualenvs/augur_env/. Please activate and restart the installation using your shell's appropriate command. ***"
                  echo "*** For example, if you're using bash, run '$HOME/.virtualenvs/source augur_env/bin/activate'. ***"
                  echo
                  exit 0
                ;;
              "No" )
                  echo
                  echo "Please create the virtual environment and return to the installation when you're finished."
                  echo "When you're creating the environment, please do not create it inside this directory. The recommended location is `$HOME`/.virtualenvs."
                  echo
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
else
  echo "Virtual environment detected under `echo $VIRTUAL_ENV`. Resuming installation..."
fi

# echo
# echo "**********************************"
# echo "Installing backend dependencies..."
# echo "**********************************"
# echo

# rm -rf build/*; rm -rf dist/*; rm $VIRTUAL_ENV/bin/*worker*;
# pip install pipreqs sphinx xlsxwriter; 
# pip install -e .; 
# pip install xlsxwriter; 
# pip install ipykernel; 
# python -m ipykernel install --user --name augur --display-name "Python (augur)"; 
# npm install apidoc;
# python setup.py install;

# echo
# echo "**********************************"
# echo "Installing workers and their dependencies..."
# echo "**********************************"
# echo
# for OUTPUT in $(ls -d workers/*/)
# do
#     if [[ $OUTPUT == *"_worker"* ]]; then
#         cd $OUTPUT
#         echo "Running setup for $(basename $(pwd))"
#         rm -rf build/*;
#         rm -rf dist/*;
#         python setup.py install;
#         pip install -e .
#         cd ../..
#     fi
# done

# echo "Would you like to install Augur's frontend dependencies?"
# select choice in "Yes" "No"
# do
#   case $choice in
#     "Yes" )
#       echo
#       echo "**********************************"
#       echo "Installing frontend dependencies..."
#       echo "**********************************"
#       echo
#       cd frontend/;
#       npm install brunch canvas vega @vue/cli;
#       npm install; 
#       npm run build;
#       cd ../;
#       break
#       ;;
#     "No" )
#       echo "Skipping frontend dependencies..."
#       break
#       ;;
#    esac
# done

# echo
# echo "**********************************"
# echo "Setting up API documentation..."
# echo "**********************************"
# echo

# cd docs && apidoc --debug -f "\.py" -i ../augur/ -o api/; rm -rf ../frontend/public/api_docs; mv api ../frontend/public/api_docs; cd ..


on_command_line=false
echo
echo "Would you like to enter your DB credentials at the command line or on a web page?"
select choice in "Command Line" "Webpage"
do
  case $choice in
    "Command Line" )
        util/scripts/install/setup_db.sh
        break
      ;;
    "Webpage" )
        echo "Continuing installation via a webpage..."
        cd util/scripts/install
        python server.py
        python make_config.py
        rm temp.config.json
        break
      ;;
  esac
done


echo "*** INSTALLATION COMPLETE ***"
