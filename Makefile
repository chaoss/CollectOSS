.PHONY: all test clean install python-docs api-docs python-docs dev-start dev-stop
.PHONY: dev-restart monitor monitor-backend monitor-frontend upgrade
.PHONY: frontend install-ubuntu-dependencies version

SERVECOMMAND=augur run
OLDVERSION="null"
EDITOR?="vi"
MODEL=**
AUGUR_PIP?='pip'
AUGUR_PYTHON?='python'
AUGUR_PIP?='pip'

default:
	@ echo "Installation Commands:"
	@ echo "    install                         Installs augur using pip"
	@ echo "    clean                           Cleans the developer environment"
	@ echo "    upgrade                         Pulls newest version, installs, performs migrations"
	@ echo "    version                         Print the currently installed version"
	@ echo "    config                          Creates a new augur.config.json"
	@ echo
	@ echo "Development Commands:"
	@ echo "    dev                             Starts the full stack and monitors the logs"
	@ echo "    dev-start                       Runs 'make serve' and 'brunch w -s' in the background"
	@ echo "    dev-stop                        Stops the backgrounded commands"
	@ echo "    dev-restart                     Runs dev-stop then dev-restart"
	@ echo
	@ echo "Testing Commands:"
	@ echo "    test                            Runs all pytest unit tests and API tests"
	@ echo "    test-functions MODEL={model}    Run pytest unit tests for the specified metrics model. Defaults to all"
	@ echo "    test-routes MODEL={model}       Run API tests for the specified metrics model. Defaults to all"
	@ echo
	@ echo "Documentation Commands:"
	@ echo "    python-docs                     Generates new Sphinx documentation"
	@ echo "    api-docs                        Generates new apidocjs documentation"
	@ echo "    docs                            Generates all documentation"
	@ echo
	@ echo "Prototyping:"
	@ echo "    jupyter                         Launches the jupyter"
	@ echo "    create-jupyter-env              Creates a jupyter environment for Augur"
	@ echo
	@ echo "Upgrade/Migration Helpers:"
	@ echo "    to-json                         Converts old augur.cfg to new augur.config.json"
	@ echo "    to-env                          Converts augur.config.json to a script that exports those values as environment variables"



#
#  Installation
#
install:
	@ ./util/scripts/install/install.sh

version:
	$(eval OLDVERSION=$(shell $(AUGUR_PYTHON) ./util/print-version.py))
	@ echo "installed version: $(OLDVERSION)"

upgrade: version install-dev
	@ $(AUGUR_PYTHON) util/post-upgrade.py $(OLDVERSION)
	@ echo "Upgraded from $(OLDVERSION) to $(shell $(AUGUR_PYTHON) util/print-version.py)."

config:
	@ bash -c '$(AUGUR_PYTHON) util/make-config.py'


#
#  Development
#
dev-start: dev-stop
	@ mkdir -p logs runtime
	@ bash -c '$(SERVECOMMAND) >logs/backend.log 2>&1 & echo $$! > logs/backend.pid;'
	@ bash -c 'sleep 4; cd frontend; npm run serve >../logs/frontend.log 2>&1 & echo $$! > ../logs/frontend.pid'
	@ echo "Server     Description       Log                   Monitoring                   PID                        "
	@ echo "------------------------------------------------------------------------------------------                 "
	@ echo "Frontend   Brunch            logs/frontend.log     make monitor-backend         $$( cat logs/frontend.pid ) "
	@ echo "Backend    Augur/Gunicorn    logs/backend.log      make monitor-frontend        $$( cat logs/backend.pid  ) "
	@ echo
	@ echo "Monitor both:  make monitor  "
	@ echo "Restart and monitor: make dev"
	@ echo "Restart servers:  make dev-start "
	@ echo "Stop servers:  make dev-stop "

dev-stop:
	@ bash -c 'if [[ -s logs/frontend.pid && (( `cat logs/frontend.pid` > 1 )) ]]; then printf "sending SIGTERM to node (Brunch) at PID $$(cat logs/frontend.pid); "; kill `cat logs/frontend.pid`; rm logs/frontend.pid > /dev/null 2>&1; fi;'
	@ bash -c 'if [[ -s logs/backend.pid  && (( `cat logs/backend.pid`  > 1 )) ]]; then printf "sending SIGTERM to python (Gunicorn) at PID $$(cat logs/backend.pid); "; kill `cat logs/backend.pid` ; rm logs/backend.pid  > /dev/null 2>&1; fi;'
	@ echo

dev: dev-restart monitor

monitor-frontend:
	@ less +F logs/frontend.log

monitor-backend:
	@ less +F logs/backend.log

monitor:
	@ tail -f logs/frontend.log -f logs/backend.log 2>/dev/null

dev-restart: dev-stop dev-start

server:
	@ $(AUGUR_PYTHON) -m augur.server

frontend:
	@ bash -c 'cd frontend; brunch build'
	@ bash -c '(sleep 4; cd frontend; brunch w -s >../logs/frontend.log 2>&1 & echo $$! > ../logs/frontend.pid)'

backend-stop:
	@ bash -c 'if [[ -s logs/backend.pid  && (( `cat logs/backend.pid`  > 1 )) ]]; then printf "sending SIGTERM to python (Gunicorn) at PID $$(cat logs/backend.pid); "; kill `cat logs/backend.pid` ; rm logs/backend.pid  > /dev/null 2>&1; fi;'
	@ echo

backend-start:
	@ mkdir -p logs runtime
	@ bash -c '$(SERVECOMMAND) >logs/backend.log 2>&1 & echo $$! > logs/backend.pid;'

backend-restart: backend-stop backend-start

backend: backend-restart

test: test-functions test-routes

test-functions:
	@ bash -c '$(AUGUR_PYTHON) -m pytest -ra -s augur/metrics/$(MODEL)/test_$(MODEL)_functions.py'

test-routes:
	@ python test/api/test_api.py $(MODEL)

# 
# Documentation
# 
python-docs:
	@ bash -c 'cd docs/ && rm -rf build/ && make html;'

python-docs-view: python-docs
	@ bash -c 'open docs/build/html/index.html'

api-docs:
	@ bash -c 'cd docs && apidoc --debug -f "\.py" -i ../augur/ -o api/; rm -rf ../frontend/public/api_docs; mv api ../frontend/public/api_docs'

api-docs-view: api-docs
	@ bash -c "open frontend/public/api_docs/index.html"

docs: api-docs python-docs

.PHONY: unlock
unlock:
	find . -type f -name "*.lock" -delete

clean:
	@ echo "Removing node_modules, logs, caches, and some other dumb stuff that can be annoying..."
	@ rm -rf runtime node_modules frontend/node_modules frontend/public augur.egg-info .pytest_cache logs 
	@ find . -name \*.pyc -delete

rebuild: clean
	@ util/scripts/install/rebuild.sh




#
#  Prototyping
#
jupyter:
		@ bash -c 'cd notebooks; jupyter notebook'

create-jupyter-env:
		bash -c '$(AUGUR_PYTHON) -m ipykernel install --user --name augur --display-name "Python (augur)";'


#
#  Upgrade helpers
#
.PHONY: to-json
to-json:
	@ bash -c '$(AUGUR_PYTHON) util/post-upgrade.py migrate_config_to_json'

.PHONY: to-env
to-env:
	@ bash -c 'AUGUR_EXPORT_ENV=1; AUGUR_INIT_ONLY=1; augur'



#
#  System-specific
#
install-ubuntu-dependencies:
	@ echo "Downloading NodeSource Installer..."
	curl -sL https://deb.nodesource.com/setup_8.x | sudo -E bash -
	@ echo "Installing Node..."
	sudo apt-get install nodejs
	@ echo "Downloading Anaconda Installer..."
	curl -SL https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh > /tmp/conda.sh
	@ echo "Installing Anaconda..."
	bash /tmp/conda.sh
	@ echo "Done. Please note the 'conda' command must be in your path for Makefile commands to work"


install-os-x-dependencies:
	@ echo "Downloading dependencies..."
	brew install node
	@ echo "Downloading Anaconda installer to ~/Downloads..."
	curl -SL https://repo.continuum.io/miniconda/Miniconda3-latest-MacOSX-x86_64.sh > /tmp/conda.sh
	@ echo "Installing Anaconda..."
	bash /tmp/conda.sh
	@ echo "Done. Please note the 'conda' command must be in your path for Makefile commands to work"
