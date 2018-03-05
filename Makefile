.PHONY: all test clean install install-dev python-docs api-docs docs dev-start dev-stop dev-restart monitor monitor-backend monitor-frontend download-upgrade upgrade

SHELL=/bin/bash
PY2 := $(shell command -v pip2 2> /dev/null)
PY3 := $(shell command -v pip3 2> /dev/null)
NODE := $(shell command -v npm 2> /dev/null)
CONDA := $(shell command -v conda 2> /dev/null)

SERVECOMMAND=gunicorn -w`getconf _NPROCESSORS_ONLN` -b0.0.0.0:5000 ghdata.server:app

CONDAUPDATE=""
CONDAACTIVATE=""
ifdef CONDA
		CONDAUPDATE=if ! source activate ghdata; then conda env create -n=ghdata -f=environment.yml && source activate ghdata; else conda env update -n=ghdata -f=environment.yml && source activate ghdata; fi;
		CONDAACTIVATE=source activate ghdata;
endif

default:
	@ echo "Commands:"
	@ echo
	@ echo "    install          Installs ghdata using pip"
	@ echo "    install-dev      Installs ghdata's developer dependencies (requires npm and pip)"
	@ echo "    install-msr      Installs MSR14 dataset"
	@ echo "    upgrade          Pulls newest version and installs"
	@ echo "    test             Run pytest unit tests"
	@ echo "    serve            Runs using gunicorn"
	@ echo "    dev              Starts the full stack and monitors the logs"
	@ echo "    dev-start        Runs 'make serve' and 'brunch w -s' in the background"
	@ echo "    dev-stop         Stops the backgrounded commands"
	@ echo "    dev-restart      Runs dev-stop then dev-restart"
	@ echo "    python-docs      Generates new Sphinx documentation"
	@ echo "    api-docs         Generates new apidocjs documentation"
	@ echo "    docs             Generates all documentation"
	@ echo "    build            Builds documentation and frontend - use before pushing"
	@ echo "    update-deps      Generates updated requirements.txt and environment.yml"
	@ echo

conda:


install: conda
		$(CONDAUPDATE) pip install --upgrade .

install-dev: conda
		$(CONDAUPDATE) pip install pipreqs sphinx
ifdef PY2
	  pip2 install --upgrade -e .
endif
ifdef PY3
		$(CONDAACTIVATE) pip3 install --upgrade -e .
endif
ifndef PY2
ifndef PY3
		 $(CONDAACTIVATE) pip install --upgrade -e .
endif
endif
ifdef NODE
		npm install -g apidoc brunch yarn
		cd frontend/ && yarn install
endif

install-msr:
		@ ./docs/install-msr.sh

download-upgrade:
		git pull

upgrade: download-upgrade install
		@ echo "Upgraded."

ugh:
		

dev-start: dev-stop
ifdef CONDA
		@ bash -c '(cd frontend; brunch w -s >../logs/frontend.log 2>&1 & echo $$! > ../logs/frontend.pid);'
		@ bash -c '(source activate ghdata; $(SERVECOMMAND) >logs/backend.log 2>&1 & echo $$! > logs/backend.pid);'
else
		@ bash -c '(cd frontend; brunch w -s >../logs/frontend.log 2>&1 & echo $$! > ../logs/frontend.pid);'
		@ bash -c '($(SERVECOMMAND) >logs/backend.log 2>&1 & echo $$! > logs/backend.pid);'
endif
		@ echo "Server     Description       Log                   Monitoring                   PID                        "
		@ echo "------------------------------------------------------------------------------------------                 "
		@ echo "Frontend   Brunch            logs/frontend.log     make monitor-backend         $$( cat logs/frontend.pid ) "
		@ echo "Backend    GHData/Gunicorn   logs/backend.log      make monitor-frontend        $$( cat logs/backend.pid  ) "
		@ echo
		@ echo "Monitor both:  make monitor  "
		@ echo "Restart and monitor: make dev"
		@ echo "Restart servers:  make dev-start "
		@ echo "Stop servers:  make dev-stop "

dev-stop:
		@ if [[ -s logs/frontend.pid && (( `cat logs/frontend.pid` > 1 )) ]]; then printf "sending SIGTERM to node (Brunch) at PID $$(cat logs/frontend.pid); "; kill `cat logs/frontend.pid`; rm logs/frontend.pid > /dev/null 2>&1; fi;
		@ if [[ -s logs/backend.pid  && (( `cat logs/backend.pid`  > 1 )) ]]; then printf "sending SIGTERM to python (Gunicorn) at PID $$(cat logs/backend.pid); "; kill `cat logs/backend.pid` ; rm logs/backend.pid  > /dev/null 2>&1; fi;
		@ echo

dev: dev-restart monitor
	@ read -p "Would you like to restart and continue monitoring? [y/n]: " -n 1 -r; \
		echo; if [[ $$REPLY =~ ^[Yy]$$ ]]; then $(MAKE) dev; fi;

monitor-frontend:
		@ less +F logs/frontend.log

monitor-backend:
		@ less +F logs/backend.log

monitor:
		@ tail -f logs/frontend.log -f logs/backend.log 2>/dev/null

dev-restart: dev-stop dev-start

serve:
ifdef CONDA
		bash -c "$(SERVECOMMAND)"
else
		gunicorn -w`getconf _NPROCESSORS_ONLN` -b0.0.0.0:5000 ghdata.server:app
endif

python-docs:
		cd docs/python   \
		&& rm -rf _build \
		&& make html

api-docs:
		apidoc --debug -f "\.py" -i ghdata/ -o docs/api/

docs: api-docs python-docs

build: docs
		cd ghdata/static/ && brunch build --production

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
		python -m pytest

update-deps:
		@ hash pipreqs 2>/dev/null || { echo "This command needs pipreqs, installing..."; pip install pipreqs; exit 1; }
		pipreqs ./
ifdef CONDA
		conda env export > environment.yml
endif