.PHONY: all test clean install install-dev python-docs api-docs docs dev-start dev-stop 
.PHONY: dev-restart monitor monitor-backend monitor-frontend download-upgrade upgrade build-metrics-status
.PHONY: frontend install-ubuntu-dependencies metric-status edit-metrics-status version

SERVECOMMAND=augur
CONDAUPDATE=if ! source activate augur; then conda env create -n=augur -f=environment.yml && source activate augur; else conda env update -n=augur -f=environment.yml && conda activate augur; fi;
CONDAACTIVATE=source activate augur;
CONDAUPDATE=. $(shell conda info --root)/etc/profile.d/conda.sh; if ! conda activate augur; then conda env create -n=augur -f=environment.yml && conda activate augur; else conda env update -n=augur -f=environment.yml && conda activate augur; fi;
CONDAACTIVATE=. $(shell conda info --root)/etc/profile.d/conda.sh; conda activate augur;
OLDVERSION="null"
EDITOR?="vi"
SOURCE=*

default:
	@ echo "Installation Commands:"
	@ echo "    install                Installs augur using pip"
	@ echo "    install-e              Installs augur in editable mode (pip -e)"
	@ echo "    install-dev            Installs augur's developer dependencies (requires npm and pip)"
	@ echo "    install-msr            Installs MSR14 dataset"
	@ echo "    upgrade                Pulls newest version, installs, performs migrations"
	@ echo "    version                Print the currently installed version"
	@ echo
	@ echo "Development Commands:"
	@ echo "    dev                    Starts the full stack and monitors the logs"
	@ echo "    dev-start              Runs 'make serve' and 'brunch w -s' in the background"
	@ echo "    dev-stop               Stops the backgrounded commands"
	@ echo "    dev-restart            Runs dev-stop then dev-restart"
	@ echo "    server            	   Runs a single instance of the server (useful for debugging endpoints)"
	@ echo "    test SOURCE={source}   Run pytest unit tests for the specified source file. Defaults to all"
	@ echo "    test-api   			       Run API tests locally using newman"
	@ echo "    build                  Builds documentation and frontend - use before pushing"
	@ echo "    frontend               Builds frontend with Brunch"
	@ echo "    update-deps            Generates updated requirements.txt and environment.yml"
	@ echo "    python-docs            Generates new Sphinx documentation"
	@ echo "    api-docs               Generates new apidocjs documentation"
	@ echo "    docs                   Generates all documentation"
	@ echo
	@ echo "Prototyping:"
	@ echo "    jupyter                Launches the jupyter"
	@ echo "    create-jupyter-env     Creates a jupyter environment for Augur"
	@ echo 
	@ echo "Upgrade/Migration Helpers:"
	@ echo "    to-json                Converts old augur.cfg to new augur.config.json"
	@ echo "    to-env                 Converts augur.config.json to a script that exports those values as environment variables"



# 
#  Installation
#
install:
	bash -c '$(CONDAUPDATE) pip install --upgrade .'

install-dev:
	bash -c '$(CONDAUPDATE) pip install pipreqs sphinx; npm install -g apidoc brunch; pip install -e .; python -m ipykernel install --user --name augur --display-name "Python (augur)"; cd frontend/ && npm install'

install-dev-admin:
	bash -c '$(CONDAUPDATE) sudo pip install pipreqs sphinx; sudo npm install -g apidoc brunch; pip install -e .; cd frontend/ && npm install'

install-msr:
	@ ./util/install-msr.sh

version:
	$(eval OLDVERSION=$(shell python ./util/print-version.py))
	@ echo "installed version: $(OLDVERSION)"

download-upgrade:
	git pull

upgrade: version download-upgrade install-dev
	@ python util/post-upgrade.py $(OLDVERSION)
	@ echo "Upgraded from $(OLDVERSION) to $(shell python util/print-version.py)."



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
	python -m augur.server

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

test:
	bash -c '$(CONDAACTIVATE) python -m pytest test/test_${SOURCE}.py'

test-api:
	make dev-start
	python test/test_api.py
	make dev-stop

.PHONY: unlock
unlock:
	find . -type f -name "*.lock" -delete

update-deps:
	@ hash pipreqs 2>/dev/null || { echo "This command needs pipreqs, installing..."; pip install pipreqs; exit 1; }
	pipreqs ./augur/
	bash -c "$(CONDAACTIVATE) conda env export > environment.yml"



# 
#  Prototyping
#
jupyter:
		@ bash -c '$(CONDAACTIVATE) cd notebooks; jupyter notebook'

create-jupyter-env:
		bash -c '$(CONDAACTIVATE) python -m ipykernel install --user --name augur --display-name "Python (augur)";'



# 
#  Upgrade helpers
#
.PHONY: to-json
to-json:
	@ bash -c '$(CONDAACTIVATE) python util/post-upgrade.py migrate_config_to_json'

.PHONY: to-env
to-env:
	@ bash -c '$(CONDAACTIVATE) AUGUR_EXPORT_ENV=1; AUGUR_INIT_ONLY=1; augur'



# 
#  System-specific
#
install-ubuntu-dependencies:
	@ echo "Downloading NodeSource Installer..."
	curl -sL https://deb.nodesource.com/setup_8.x | sudo -E bash -
	@ echo "Installing Node and MariaDB..."
	sudo apt-get install nodejs mariadb-server
	@ echo "Downloading Anaconda Installer..."
	curl https://repo.anaconda.com/archive/Anaconda3-5.1.0-Linux-x86_64.sh | bash -e

install-os-x-dependencies:
	@ echo "Downloading dependencies..."
	brew install node mariadb wget
	@ echo "Downloading Anaconda installer to ~/Downloads..."
	cd ~/Downloads && wget https://repo.anaconda.com/archive/Anaconda3-5.1.0-MacOSX-x86_64.pkg
	cd ~/Downloads && open Anaconda3-5.1.0-MacOSX-x86_64.pkg