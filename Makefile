.PHONY: all test clean install install-dev python-docs api-docs docs dev-start dev-stop dev-restart download-upgrade upgrade

SHELL=/bin/bash
PY2 := $(shell command -v pip2 2> /dev/null)
PY3 := $(shell command -v pip3 2> /dev/null)
NODE := $(shell command -v npm 2> /dev/null)
CONDA := $(shell command -v conda 2> /dev/null)

CONDAUPDATE=""
CONDAACTIVATE=""
ifdef CONDA
		@ echo "Detected Anaconda, updating environment..."
		CONDAUPDATE="if ! source activate ghdata; then conda env create -n=ghdata -f=environment.yml && source activate ghdata; else conda env update -n=ghdata -f=environment.yml && source activate ghdata; fi;"
		CONDAACTIVATE="source activate ghdata;"
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
	@ echo "    dev-start        Starts GHData and Brunch screen sessions"
	@ echo "    dev-stop         Kills GHData and Brunch screen sessions"
	@ echo "    python-docs      Generates new Sphinx documentation"
	@ echo "    api-docs         Generates new apidocjs documentation"
	@ echo "    docs             Generates all documentation"
	@ echo "    build            Builds documentation and frontend"
	@ echo "    update-deps      Generates updated requirements.txt and environment.yml"
	@ echo

conda:


install: conda
		$(CONDAUPDATE) pip install --upgrade .

install-dev: conda
		$(CONDAUPDATE) pip install pipreqs || (echo "Install failed. Trying again with sudo..." && sudo pip install pipreqs)
ifdef PY2
	  pip2 install --upgrade .
endif
ifdef PY3
		$(CONDAACTIVATE) pip3 install --upgrade .
endif
ifndef PY2
ifndef PY3
		 $(CONDAACTIVATE) pip install --upgrade .
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

dev-start:
ifdef CONDA
		screen -d -S "ghdata-backend" -m bash -c "source activate ghdata && export GHDATA_DEBUG=1 && python -m ghdata.server"
else
		screen -d -S "ghdata-backend" -m bash -c "export GHDATA_DEBUG=1 && python -m ghdata.server"
endif
		screen -d -S "ghdata-frontend" -m bash -c "cd frontend && brunch watch -s -n"
		@ printf '\nDevelopment servers started.\n\nBrunch server  |  Port: 3333      To see log: screen -r "ghdata-frontend"\nGHData         |  Port: 5000      To see log: screen -r "ghdata-backend"\n\n'
dev-start-public:
		screen -d -S "ghdata-backend" -m bash -c "export GHDATA_DEBUG=1 && export GHDATA_HOST='0.0.0.0' && python -m ghdata.server"
		screen -d -S "ghdata-frontend" -m bash -c "cd frontend && brunch watch -s -n"
		@ printf '\nDevelopment servers started. If ports 5000 and 3333 are open on your firewall, these will be avalible network-wide\n\nBrunch server  |  Port: 3333      To see log: screen -r "ghdata-frontend"\nGHData         |  Port: 5000      To see log: screen -r "ghdata-backend"\n\n'

dev-stop:
		screen -S "ghdata-backend" -X kill
		screen -S "ghdata-frontend" -X kill

dev-restart: dev-stop dev-start

serve:
ifdef CONDA
		source activate ghdata && gunicorn -w`getconf _NPROCESSORS_ONLN` -b0.0.0.0:5000 ghdata.server:app
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
		cd ghdata/static/ && brunch build

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
ifdef PY2
		python2 -m pytest
else
		@ echo "Python 2 not installed, skipping..."
endif
ifdef PY3
		python3 -m pytest
else
		@ echo "Python 3 not installed, skipping..."
endif

update-deps:
		@ hash pipreqs 2>/dev/null || { echo "This command needs pipreqs, installing..."; pip install pipreqs; exit 1; }
		pipreqs ./
ifdef CONDA
		conda env export > environment.yml
endif