#SPDX-License-Identifier: MIT
FROM python:3.8.9-slim-buster as build-stage

COPY ./util/docker/backend/install_packages.sh .
RUN ./install_packages.sh

LABEL maintainer="outdoors@acm.org"
LABEL version="0.2.0"

WORKDIR /augur

COPY ./README.md .
COPY ./augur/ augur/
COPY ./metadata.py .
COPY ./setup.py .
COPY ./scripts/ scripts/
COPY ./workers/ workers/

COPY ./schema/ schema/ 

RUN pip install .
RUN ./scripts/install/workers.sh 

COPY ./util/docker/backend/backend.docker.config.json .

#Needs to be hardcoded or the API doesn't work.
EXPOSE 5000
RUN augur config init --rc-config-file backend.docker.config.json; mkdir repos/;

#Load environment variables at runtime.
CMD bash -c "if [ \"$AUGUR_DB_SCHEMA_BUILD\" == \"1\" ]; then augur db create-schema; fi; augur config init --db_name \"$AUGUR_DB_NAME\" --db_port \"$AUGUR_DB_PORT\" --db_user \"$AUGUR_DB_DB_USER\" --db_password \"$AUGUR_DB_PASSWORD\" --github_api_key \"$AUGUR_GITHUB_API_KEY\"; augur backend start"