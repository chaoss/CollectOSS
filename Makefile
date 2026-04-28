#SPDX-License-Identifier: MIT

default:
	@ echo "Testing Commands:"
	@ echo "    test-data                       Start the testing dataset Docker database"
	@ echo "    test                            Runs all tests"
	@ echo "    test-api                        Run all API tests"
	@ echo
	@ echo "Documentation Commands:"
	@ echo "    docs                            Generates the documentation"
	@ echo "    docs-view                       Generates the documentation, then opens it for local viewing"

lint:
	@ pylint collectoss
lint-count:
	@ pylint collectoss | wc -l
lint-docs:
	@ pylint collectoss | grep docstring
lint-docs-missing:
	@ pylint collectoss | grep docstring | wc -l

lint-github-tasks-count:
	@ pylint collectoss | grep collectoss/tasks/github/ | wc -l

#
# Testing
#
.PHONY: test test-data test-application test-metric-routes test-python-versions

test-data:
	@ - docker stop augur_test_data
	@ - docker rm augur_test_data
	@ docker run -p 5434:5432 --name augur_test_data augurlabs/augur:test_data@sha256:71da12114bf28584a9a64ede2fac0cbc8dffc8e2f4a2c61231206e2f82201c2f

test:
	# @ pytest tests/test_tasks/test_github_tasks/
	@ python3 tests/start_server.py
	@ pytest tests/test_metrics/test_metrics_functionality/ tests/test_routes/test_api_functionality/ tests/test_tasks/ tests/test_application/ 
	@ python3 tests/stop_server.py

test-api:
	@ python3 tests/start_server.py
	@ pytest tests/test_metrics/test_metrics_functionality/ tests/test_routes/test_api_functionality/
	@ python3 tests/stop_server.py
	





#
# UV installation
#
.PHONY: uv
uv:
	@ command -v uv >/dev/null 2>&1 || { echo "Installing uv..."; pip install --user uv; }

#
# Documentation
#
.PHONY: docs docs-view
docs: uv
	-rm -rf docs/build
	uv run --only-group docs make -C docs html

docs-view: docs
	@ bash -c 'open docs/build/html/index.html'
