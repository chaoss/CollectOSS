#!/bin/bash
## Back End

if [[ -z $VIRTUAL_ENV ]]; then
  echo "*** We noticed you're not using a virutal environment. It is STRONGLY recommended to install Augur in its own virutal environment. ***"
  echo "*** Would you like to create a virtual environment using virtualenv? ***"
  read  -n 1 -p "[y/n]: " mainmenuinput
  echo

  if [[ $mainmenuinput == 'y' ]]; then
    # virtualenv venv/augur
    echo "*** Your environment was installed to venv/augur. Please activate and restart the installation. ***"
    echo "*** For example, if you're using bash run 'source venv/augur/bin/activate'. ***"
    exit 0
  fi

else
  echo "Virtual environment detected. Resuming installation."
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

echo "Installing frontend dependencies..."
cd frontend/;
yarn install;
yarn global add apidoc brunch newman @vue/cli; 
yarn run build;
cd ../;

echo "Setting up API documentation..."
cd docs && apidoc --debug -f "\.py" -i ../augur/ -o api/; rm -rf ../frontend/public/api_docs; mv api ../frontend/public/api_docs;
