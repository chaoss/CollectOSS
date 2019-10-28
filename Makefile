SERVE_COMMAND=augur run
ENABLE_HOUSEKEEPER=--enable-housekeeper
OLDVERSION="null"
EDITOR?="vi"
MODEL=**
AUGUR_PIP?='pip'
AUGUR_PYTHON?='python'

default:
	@ echo "Installation Commands:"
	@ echo "    install                         Installs augur using pip"
	@ echo "    version                         Print the currently installed version"
	@ echo "    config                          Creates a new augur.config.json"
	@ echo "    clean                           Removes potentially troublesome compiled files"
	@ echo "    rebuild                         Removes build/compiled files & binaries and reinstalls the project"
	@ echo
	@ echo "Development Commands:"
	@ echo "    dev                             Starts the full stack and monitors the logs"
	@ echo "    dev-start                       Runs the backend and frontend servers in the background"
	@ echo "    dev-stop                        Stops the backgrounded backend & frontend server commands"
	@ echo "    dev-restart                     Runs dev-stop then dev-start"
	@ echo
	@ echo "Testing Commands:"
	@ echo "    test MODEL={model}              Runs all pytest unit tests and API tests for the specified metrics model. Defaults to all"
	@ echo "    test-functions MODEL={model}    Run pytest unit tests for the specified metrics model. Defaults to all"
	@ echo "    test-routes MODEL={model}       Run API tests for the specified metrics model. Defaults to all"
	@ echo
	@ echo "Documentation Commands:"
	@ echo "    sphinx-docs                     Generates the documentation using sphinx"
	@ echo "    api-docs                        Generates the REST API documentation using apidocjs"
	@ echo "    docs                            Generates all documentation"


#
#  Installation
#
.PHONY: install version config
install:
	@ ./util/scripts/install/install.sh

version:
	$(eval OLDVERSION=$(shell $(AUGUR_PYTHON) ./util/print-version.py))
	@ echo "installed version: $(OLDVERSION)"

config:
	@ ./util/scripts/install/config.sh

clean:
	@ echo "Removing node_modules, logs, caches, and some other dumb stuff that can be annoying..."
	@ rm -rf runtime node_modules frontend/node_modules frontend/public augur.egg-info .pytest_cache logs 
	@ find . -name \*.pyc -delete
	@ find . -type f -name "*.lock" -delete

rebuild: clean
	@ util/scripts/install/rebuild.sh


#
#  Development
#
.PHONY: dev-start dev-stop dev monitor-frontend monitor-backend monitor frontend backend-stop backend-start backend-restart backend clean rebuild
dev-start: dev-stop
	@ mkdir -p logs runtime
	@ bash -c '$(SERVE_COMMAND) $(ENABLE_HOUSEKEEPER) >logs/backend.log 2>&1 & echo $$! > logs/backend.pid;'
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

frontend:
	@ bash -c 'cd frontend; npm run serve'

backend-stop:
	@ bash -c 'if [[ -s logs/backend.pid  && (( `cat logs/backend.pid`  > 1 )) ]]; then printf "sending SIGTERM to python (Gunicorn) at PID $$(cat logs/backend.pid); "; kill `cat logs/backend.pid` ; rm logs/backend.pid  > /dev/null 2>&1; fi;'
	@ echo

backend-start:
	@ mkdir -p logs runtime
	@ bash -c '$(SERVE_COMMAND) $(ENABLE_HOUSEKEEPER) >logs/backend.log 2>&1 & echo $$! > logs/backend.pid;'

backend-restart: backend-stop backend-start

backend: backend-restart


#
# Testing
#
.PHONY: test test-functions test-routes
test: test-functions test-routes

test-functions:
	@ bash -c '$(AUGUR_PYTHON) -m pytest -ra -s augur/metrics/$(MODEL)/test_$(MODEL)_functions.py'

test-routes:
	@ $(AUGUR_PYTHON) test/api/test_api.py $(MODEL)


# 
# Documentation
# 
.PHONY: sphinx-docs sphinx-docs-view api-docs api-docs-view docs
sphinx-docs:
	@ bash -c 'cd docs/ && rm -rf build/ && make html;'

sphinx-docs-view: sphinx-docs
	@ bash -c 'open docs/build/html/index.html'

api-docs:
	@ bash -c 'cd docs && apidoc -f "\.py" -i ../augur/ -o api/; rm -rf ../frontend/public/api_docs; mv api ../frontend/public/api_docs'

api-docs-view: api-docs
	@ bash -c "open frontend/public/api_docs/index.html"

docs: api-docs sphinx-docs
