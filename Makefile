SERVE_COMMAND=augur run
ENABLE_HOUSEKEEPER=--enable-housekeeper
OLDVERSION="null"
EDITOR?="vi"
AUGUR_PIP?='pip'
AUGUR_PYTHON?='python'

DOCKER_IMAGE_NAME?='augurlabs/augur'
DOCKER_IMAGE_TAG?='latest'
DOCKER_CONTAINER_NAME?='augurlabs/augur'
AUGUR_PORT?=5000

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
	@ echo "    test                            Runs all unit tests and API tests"
	@ echo "    test-metrics                    Run unit tests for the specified metrics model"
	@ echo "    test-metrics-api                Run API tests for the specified metrics model"
	@ echo
	@ echo "Documentation Commands:"
	@ echo "    library-docs                    Generates the documentation using sphinx"
	@ echo "    api-docs                        Generates the REST API documentation using apidocjs"
	@ echo "    docs                            Generates all documentation"


#
#  Installation
#
.PHONY: install version config
install:
	@ ./util/scripts/install/install.sh

install-spdx:
	@ ./util/scripts/install/install-spdx.sh

install-spdx-sudo:
	@ ./util/scripts/install/install-spdx-sudo.sh

install-augur-sbom:
	@ ./util/scripts/install/nomos.sh

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

augur-start:
	@ ./util/scripts/control/augur.sh

collect:
	@ ./util/scripts/control/collect.sh

run:
	@ ./util/scripts/control/augur.sh
	@ echo "Waiting for the server to start... (this will take about 3 minutes)"
	@ echo "In the meantime, consider taking a short break - you've earned it!"
	@ sleep 180
	@ ./util/scripts/control/collect.sh

status:
	@ ./util/scripts/control/status.sh

docker-build:
	@ bash -c 'docker build -t $(DOCKER_IMAGE_NAME) -f util/packaging/docker/augur/Dockerfile .'

docker-run:
	@ bash -c 'docker run -p $(AUGUR_PORT):$(AUGUR_PORT) --name $(DOCKER_CONTAINER_NAME) --env-file env.txt $(DOCKER_IMAGE_NAME):$(DOCKER_IMAGE_TAG)'




#
# Testing
#
.PHONY: test test-metrics test-metrics-api
test: test-metrics test-metrics-api

test-metrics:
	@ bash -c 'tox -e py-metrics 2>&1 | tee logs/metrics_test.log'

test-metrics-api:
	@ bash -c 'tox -e py-metrics_api 2>&1 | tee logs/metrics_api_test.log'

test-python-versions:
	@ bash -c 'tox -e ALL 2>&1 | tee logs/metrics_ALL.log'


#
# Documentation
#
.PHONY: library-docs library-docs-view api-docs api-docs-view docs
library-docs:
	@ bash -c 'cd docs/ && rm -rf build/ && make html;'

library-docs-view: library-docs
	@ bash -c 'open docs/build/html/index.html'

api-docs:
	@ util/scripts/install/api_docs.sh

api-docs-view: api-docs
	@ bash -c "open frontend/public/api_docs/index.html"

docs: api-docs library-docs
