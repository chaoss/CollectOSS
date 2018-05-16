.PHONY: all test clean install install-dev python-docs api-docs docs dev-start dev-stop dev-restart monitor monitor-backend monitor-frontend download-upgrade upgrade frontend install-ubuntu-dependencies metric-status edit-metrics-status update-upsteam

SERVECOMMAND=gunicorn -w`getconf _NPROCESSORS_ONLN` -b0.0.0.0:5000 augur.server:app
CONDAUPDATE=if ! source activate augur; then conda env create -n=augur -f=environment.yml && source activate augur && python -m ipykernel install --user --name augur --display-name "Python (augur)"; else conda env update -n=augur -f=environment.yml && conda activate augur; fi;

default:
	@ echo "Commands:"
	@ echo "    install                Installs augur using pip"
	@ echo "    install-dev            Installs augur's developer dependencies (requires npm and pip)"
	@ echo "    install-msr            Installs MSR14 dataset"
	@ echo "    upgrade                Pulls newest version and installs"
	@ echo "    test                   Run pytest unit tests"
	@ echo "    serve                  Runs using gunicorn"
	@ echo "    dev                    Starts the full stack and monitors the logs"
	@ echo "    dev-start              Runs 'make serve' and 'brunch w -s' in the background"
	@ echo "    dev-stop               Stops the backgrounded commands"
	@ echo "    dev-restart            Runs dev-stop then dev-restart"
	@ echo "    metrics-status         Shows the implementation status of CHAOSS metrics"
	@ echo "    edit-metrics-status    Edits the JSON file that tracks CHAOSS metrics implementation status"
	@ echo "    jupyter                Launches the jupyter"
	@ echo "    create-jupyter-env     Creates a jupyter environment for Augur"
	@ echo "    python-docs            Generates new Sphinx documentation"
	@ echo "    api-docs               Generates new apidocjs documentation"
	@ echo "    docs                   Generates all documentation"
	@ echo "    frontend               Builds frontend with Brunch"
	@ echo "    build                  Builds documentation and frontend - use before pushing"
	@ echo "    update-deps            Generates updated requirements.txt and environment.yml"


install:
		bash -c '$(CONDAUPDATE) pip install --upgrade .'

install-dev:
		bash -c '$(CONDAUPDATE) pip install pipreqs sphinx; npm install -g apidoc brunch; pip install -e .; cd frontend/ && npm install'

install-dev-admin:
	bash -c '$(CONDAUPDATE) sudo pip install pipreqs sphinx; sudo npm install -g apidoc brunch; pip install -e .; cd frontend/ && npm install'

install-msr:
		@ ./docs/install-msr.sh

download-upgrade:
		git pull

update-upsteam: 
	git submodule update --init --recursive

upgrade: download-upgrade update-upsteam dev-install
		@ echo "Upgraded."

dev-start: dev-stop
		@ bash -c '(source activate augur; cd frontend; brunch w -s >../logs/frontend.log 2>&1 & echo $$! > ../logs/frontend.pid;)'
		@ bash -c '(source activate augur; $(SERVECOMMAND) >logs/backend.log 2>&1 & echo $$! > logs/backend.pid;)'
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

serve:
ifdef CONDA
		bash -lc "$(SERVECOMMAND)"
else
		gunicorn -w`getconf _NPROCESSORS_ONLN` -b0.0.0.0:5000 augur.server:app
endif

frontend:
		bash -lc 'cd frontend; brunch build'

python-docs:
		cd docs/python   \
		&& rm -rf _build \
		&& make html

api-docs:
		cd docs && apidoc --debug -f "\.py" -i ../augur/ -o api/

docs: api-docs python-docs

build: frontend docs
		cd augur/static/ && brunch build --production

check-test-env:
ifndef DB_TEST_URL
	@ printf "Please set DB_TEST_URL to a valid database string. It should look like:\n\
	\n\
	    mysql+pymysql://<username>:<pass>@<host>:<post>/<database>\n\n"
	@ exit 1
endif

ifndef PUBLIC_WWW_TEST_API_KEY
	@ printf "Please set PUBLIC_WWW_TEST_API_KEY to a valid API key. Get one here:\n\
	\n\
	    https://publicwww.com/\n\n"
	@ exit 1
endif

test: check-test-env
		python -m pytest ./test

update-deps:
		@ hash pipreqs 2>/dev/null || { echo "This command needs pipreqs, installing..."; pip install pipreqs; exit 1; }
		pipreqs ./
ifdef CONDA
		conda env export > environment.yml
endif

metrics-status: update-upsteam
	@ cd docs/metrics/ && python status.py | less

edit-metrics-status:
	$(EDITOR) docs/metrics/status.json

jupyter:
		@ bash -c 'source activate augur; cd notebooks; jupyter notebook'

create-jupyter-env:
		python -m ipykernel install --user --name augur --display-name "Python (augur)";

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