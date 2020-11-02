#SPDX-License-Identifier: MIT
FROM python:3.6-slim-buster as build-stage

COPY ./util/docker/backend/install_packages.sh .
RUN ./install_packages.sh

LABEL maintainer="c@carterlandis.com"
LABEL version="0.1.0"

WORKDIR /augur

COPY ./README.md .
COPY ./augur/ augur/
COPY ./metadata.py .
COPY ./setup.py .
COPY ./scripts/ scripts/
COPY ./workers/ workers/

RUN pip install .
RUN ./scripts/install/workers.sh prod

COPY ./util/docker/backend/backend.docker.config.json .
RUN augur config init --rc-config-file backend.docker.config.json; mkdir repos/;

CMD augur db update-api-key docker_key; augur backend start
