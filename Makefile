.PHONY: all test clean install install-dev python-docs api-docs docs

default:
	@ printf "Please type a valid command.\n\
	\n\
	\e[1minstall \e[0m     Installs ghdata using pip\n\
	\e[1minstall-dev \e[0m Installs ghdata's developer dependencies (requires npm and pip)\n\
	\e[1mtest \e[0m        Run unit tests\n\
	\e[1mrun-debug \e[0m   Runs GHData in development mode\n\
	\e[1mpython-docs \e[0m Generates new Sphinx documentation\n\
	\e[1mapi-docs \e[0m    Generates new apidocjs documentation\n\
	\e[1mdocs \e[0m        Generates all documentation\n"

install:
		sudo pip2 install --upgrade . && pip3 install --upgrade .

install-dev: install
		npm install -g apidoc

run-debug:
		export FLASK_APP=ghdata.server &&\
		export FLASK_DEBUG=1 &&\
		flask run --host 0.0.0.0

python-docs:
		cd docs/python   \
		&& rm -rf _build \
		&& make html

api-docs:l
		apidoc -i ghdata/ -o docs/api/

docs: api-docs python-docs

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