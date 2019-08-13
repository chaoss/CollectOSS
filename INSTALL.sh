## Back End
rm -rf build/*; rm $VIRTUAL_ENV/bin/*worker_start*; 
pip install pipreqs sphinx; 
pip install -e .; pip install ipykernel; pip install xlsxwriter; python -m ipykernel install --user --name augur --display-name "Python (augur)"; 
python setup.py install;

## Front End 
cd frontend/;
yarn install;
yarn build; 
yarn global add apidoc brunch newman @vue/cli; 
cd ../;

## Workers
cd workers/;
cd facade_worker;
python setup.py install;
pip install .;
cd ../github_worker;
python setup.py install; 
pip install .;
cd ../insight_worker; 
python setup.py install; 
pip install .;
cd ../linux_badge_worker; 
python setup.py install;
pip install .;
cd ../pull_reqeust_worker; 
python setup.py install;
pip install .; 
cd ../repo_info_worker;
rm -rf build/*;
python setup.py install; 
pip install .;
cd ../..;

## API Docs
cd docs && apidoc --debug -f "\.py" -i ../augur/ -o api/; rm -rf ../frontend/public/api_docs; mv api ../frontend/public/api_docs;
