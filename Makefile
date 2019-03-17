.PHONY: all test clean install install-dev python-docs api-docs docs dev-start dev-stop 
.PHONY: dev-restart monitor monitor-backend monitor-frontend download-upgrade upgrade build-metrics-status
.PHONY: frontend install-ubuntu-dependencies metric-status edit-metrics-status version

SERVECOMMAND=augur
CONDAUPDATE=. $(shell conda info --root)/etc/profile.d/conda.sh; if ! conda activate augur; then conda env create -n=augur -f=environment.yml; else conda env update -n=augur -f=environment.yml; fi;
CONDAACTIVATE=. $(shell conda info --root)/etc/profile.d/conda.sh; conda activate augur;
OLDVERSION="null"
EDITOR?="vi"
SOURCE=**
AUGUR_PIP?='pip'
AUGUR_PYTHON?='python'

default:
	@ echo "Installation Commands:"
	@ echo "    install                    Installs augur using pip"
	@ echo "    install-dev                Installs augur's developer dependencies (requires npm and pip)"
	@ echo "    install-msr                Installs MSR14 dataset"
	@ echo "    upgrade                    Pulls newest version, installs, performs migrations"
	@ echo "    version                    Print the currently installed version"
	@ echo
	@ echo "Development Commands:"
	@ echo "    dev                        Starts the full stack and monitors the logs"
	@ echo "    dev-start                  Runs 'make serve' and 'brunch w -s' in the background"
	@ echo "    dev-stop                   Stops the backgrounded commands"
	@ echo "    dev-restart                Runs dev-stop then dev-restart"
	@ echo "    server            	       Runs a single instance of the server (useful for debugging)"
	@ echo "    test    			       Runs all pytest unit tests and API tests"
	@ echo "    test-ds SOURCE={source}    Run pytest unit tests for the specified data source. Defaults to all"
	@ echo "    test-api   			       Run API tests locally using newman"
	@ echo "    build                      Builds documentation and frontend - use before pushing"
	@ echo "    frontend                   Builds frontend with Brunch"
	@ echo "    update-deps                Generates updated requirements.txt and environment.yml"
	@ echo "    python-docs                Generates new Sphinx documentation"
	@ echo "    api-docs                   Generates new apidocjs documentation"
	@ echo "    docs                       Generates all documentation"
	@ echo "Git commands"
	@ echo "    update                     Pull the latest version of your current branch"
	@ echo
	@ echo "Prototyping:"
	@ echo "    jupyter                    Launches the jupyter"
	@ echo "    create-jupyter-env         Creates a jupyter environment for Augur"
	@ echo 
	@ echo "Upgrade/Migration Helpers:"
	@ echo "    to-json                    Converts old augur.cfg to new augur.config.json"
	@ echo "    to-env                     Converts augur.config.json to a script that exports those values as environment variables"



# 
#  Installation
#
install:
	bash -c '$(CONDAUPDATE) $(CONDAACTIVATE) $(AUGUR_PIP) install --upgrade .'

install-dev:
	bash -c '$(CONDAUPDATE) $(CONDAACTIVATE) $(AUGUR_PIP) install pipreqs sphinx; sudo npm install -g apidoc brunch newman; $(AUGUR_PIP) install -e .; $(AUGUR_PYTHON) -m ipykernel install --user --name augur --display-name "Python (augur)"; cd frontend/ && npm install'

install-msr:
	@ ./util/install-msr.sh

version:
	$(eval OLDVERSION=$(shell $(AUGUR_PYTHON) ./util/print-version.py))
	@ echo "installed version: $(OLDVERSION)"

download-upgrade:
	git pull

upgrade: version download-upgrade install-dev
	@ $(AUGUR_PYTHON) util/post-upgrade.py $(OLDVERSION)
	@ echo "Upgraded from $(OLDVERSION) to $(shell $(AUGUR_PYTHON) util/print-version.py)."



# 
#  Development
#
dev-start: dev-stop
	@ bash -c '($(CONDAACTIVATE) $(SERVECOMMAND) >logs/backend.log 2>&1 & echo $$! > logs/backend.pid;)'
	@ bash -c '($(CONDAACTIVATE) sleep 4; cd frontend; brunch w -s >../logs/frontend.log 2>&1 & echo $$! > ../logs/frontend.pid;)'
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
	bash -c 'cd frontend; brunch build'

python-docs:
	@ bash -c '$(CONDAACTIVATE) cd docs/python && rm -rf _build && make html; rm -rf ../../frontend/public/docs; mv build/html ../../frontend/public/docs'

api-docs:
	@ bash -c '$(CONDAACTIVATE) cd docs && apidoc --debug -f "\.py" -i ../augur/ -o api/; rm -rf ../frontend/public/api_docs; mv api ../frontend/public/api_docs'

docs: api-docs python-docs

build: frontend docs
	cd augur/static/ \
	&& brunch build --production

test:test-ds test-api

test-ds:
	bash -c '$(CONDAACTIVATE) $(AUGUR_PYTHON) -m pytest augur/datasources/$(SOURCE)/test_$(SOURCE).py'

test-api:
	make dev-start
	$(AUGUR_PYTHON) test/api/test_api.py
	make dev-stop

.PHONY: unlock
unlock:
	find . -type f -name "*.lock" -delete

update-deps:
	@ hash pipreqs 2>/dev/null || { echo "This command needs pipreqs, installing..."; $(AUGUR_PIP) install pipreqs; exit 1; }
	pipreqs ./augur/
	bash -c "$(CONDAACTIVATE) conda env  --no-builds > environment.yml"

vagrant:
	@ vagrant up
	@ vagrant ssh
	@ echo "****************************************************"
	@ echo "Don't forget to shutdown the VM with 'vagrant halt'!"
	@ echo "****************************************************"

#
# Git
#
update:
	git stash
	git pull
	git stash pop


# 
#  Prototyping
#
jupyter:
		@ bash -c '$(CONDAACTIVATE) cd notebooks; jupyter notebook'

create-jupyter-env:
		bash -c '$(CONDAACTIVATE) $(AUGUR_PYTHON) -m ipykernel install --user --name augur --display-name "Python (augur)";'



# 
#  Upgrade helpers
#
.PHONY: to-json
to-json:
	@ bash -c '$(CONDAACTIVATE) $(AUGUR_PYTHON) util/post-upgrade.py migrate_config_to_json'

.PHONY: to-env
to-env:
	@ bash -c '$(CONDAACTIVATE) AUGUR_EXPORT_ENV=1; AUGUR_INIT_ONLY=1; augur'



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
