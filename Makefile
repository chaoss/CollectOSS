.PHONY: all test clean install install-dev python-docs api-docs docs dev-start dev-stop dev-restart

default:
	@ printf "Please type a valid command.\n\
	\n\
	\e[1minstall \e[0m     Installs ghdata using pip\n\
	\e[1minstall-dev \e[0m Installs ghdata's developer dependencies (requires npm and pip)\n\
	\e[1mtest \e[0m        Run unit tests\n\
	\e[1mrun-debug \e[0m   Runs GHData in development mode\n\
	\e[1mpython-docs \e[0m Generates new Sphinx documentation\n\
	\e[1mapi-docs \e[0m    Generates new apidocjs documentation\n\
	\e[1mdocs \e[0m        Generates all documentation\n\
	\e[1mupdate-deps \e[0m Generates updated requirements.txt\n"

install:
		pip install --upgrade .

install-dev: install
	  pip2 install --upgrade .
	  pip3 install --upgrade .
		npm install -g apidoc brunch
		cd ghdata/static/ && npm install


dev-start:
		screen -d -S "ghdata-backend" -m bash -c "export GHDATA_DEBUG=1 && python -m ghdata.server"
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
		python2 -m pytest
		python3 -m pytest

update-deps:
		@ hash pipreqs 2>/dev/null || { echo "This command needs pipreqs, installing..."; pip install pipreqs; exit 1; }
		pipreqs ./