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
	@ echo "    dev                             Starts the full stack in the background"
	@ echo "    dev-start                       Runs the backend and frontend servers in the background"
	@ echo "    dev-stop                        Stops the backgrounded backend & frontend server commands"
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
	@ scripts/control/clean.sh

rebuild:
	@ scripts/control/rebuild.sh prod

rebuild-dev:
	@ scripts/control/rebuild.sh dev


#
#  Development
#
.PHONY: dev-start dev-stop dev monitor-frontend monitor-backend monitor frontend backend-stop backend-start backend-restart backend clean rebuild

dev-start: dev-stop
	@ scripts/control/start_augur.sh
	@ scripts/control/start_frontend.sh

dev-stop: 
	@ augur/cli/scripts/kill_processes.sh
	@ scripts/control/kill_frontend.sh

dev: dev-stop dev-start


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

test-db:
	@ docker run -d -p 5434:5432 --name augur_test_database augurlabs/augur:test_data

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
#
.PHONY: compose-run compose-run-database
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
	@ docker run -p 5434:5432 --name augur_database augurlabs/augur:database

