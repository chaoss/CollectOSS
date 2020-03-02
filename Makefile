SERVE_COMMAND=augur run
ENABLE_HOUSEKEEPER=--enable-housekeeper
EDITOR?="vi"
AUGUR_PIP?='pip'
AUGUR_PYTHON?='python'
AUGUR_PORT?=5000

default:
	@ echo "Installation Commands:"
	@ echo "    install                         Installs Augur's full stack for production"
	@ echo "    install                         Installs Augur's full stack for development"
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
.PHONY: install install-dev 
.PHONY: install-spdx install-spdx-sudo install-augur-sbom 
.PHONY: clean rebuild
install:
	@ ./scripts/install/install.sh prod

install-dev:
	@ ./scripts/install/install.sh dev

install-spdx:
	@ ./scripts/install/install-spdx.sh

install-spdx-sudo:
	@ ./scripts/install/install-spdx-sudo.sh

install-augur-sbom:
	@ ./scripts/install/nomos.sh

clean:
	@ scripts/install/clean.sh

rebuild:
	@ scripts/install/rebuild.sh


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
	@ bash -c 'augur util kill'
	@ echo

backend-start:
	@ mkdir -p logs runtime
	@ bash -c '$(SERVE_COMMAND) $(ENABLE_HOUSEKEEPER) >logs/backend.log 2>&1 & echo $$! > logs/backend.pid;'

backend-restart: backend-stop backend-start

backend: backend-restart

status:
	@ ./scripts/control/status.sh quick

status-interactive:
	@ ./scripts/control/status.sh interactive

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
.PHONY: library-docs library-docs-view 
.PHONY:api-docs api-docs-view docs

library-docs:
	@ bash -c 'cd docs/ && rm -rf build/ && make html;'

library-docs-view: library-docs
	@ bash -c 'open docs/build/html/index.html'

api-docs:
	@ scripts/install/api_docs.sh

api-docs-view: api-docs
	@ bash -c "open frontend/public/api_docs/index.html"

docs: api-docs library-docs


#
# Docker Shortcuts
# .PHONY: compose-run compose-run-database
.PHONY: build-backend run-backend build-frontend run-frontend build-database run-database 


compose-run:
	@ docker-compose -f docker-compose.yml up --build

compose-run-database:
	@ echo "**************************************************************************"
	@ echo "Make sure there are no database credentials in augur_env.txt!"
	@ echo "**************************************************************************"
	@ echo
	@ docker-compose -f docker-compose.yml -f database-compose.yml up --build

docker-build: docker-build-backend docker-build-frontend docker-build-database

docker-build-backend:
	@ docker build -t augurlabs/augur:backend -f util/docker/backend/Dockerfile .

docker-build-frontend:
	@ docker build -t augurlabs/augur:frontend -f util/docker/frontend/Dockerfile .

docker-build-database:
	@ docker build -t augurlabs/augur:database -f util/docker/database/Dockerfile .


docker-run-backend:
	@ docker run -d -p 5000:5000 --name augur_backend --env-file augur_env.txt augurlabs/augur:backend

docker-run-frontend:
	@ docker run -d -p 8080:8080 --name augur_frontend augurlabs/augur:frontend

docker-run-database:
	@ docker run -d -p 5432:5432 --name augur_database augurlabs/augur:database

