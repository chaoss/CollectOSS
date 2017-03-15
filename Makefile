python_docs:
		cd docs/python   \
		&& rm -rf _build \
		&& make html

api_docs:
		apidoc -i ghdata/ -o docs/api/

install_deps:
		pip install --upgrade .
		npm install -g apidoc

docs: api python