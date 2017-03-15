python:
		cd python
		rm -rf _build
		make html

api:
		apidoc -i ../ghdata/ -o ./api/

install_deps:
		pip install sphinx
		npm install -g apidoc

all: api python