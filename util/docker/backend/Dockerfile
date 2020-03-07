FROM python:3.6-slim-buster as build-stage

COPY ./util/docker/backend/install_packages.sh .
RUN ./install_packages.sh

LABEL maintainer="c@carterlandis.com"
LABEL version="0.1.0"

WORKDIR /augur

COPY ./README.md .
COPY ./requirements.txt .
COPY ./dev_requirements.txt .
COPY ./augur/ ./augur/
COPY ./scripts/ ./scripts/
COPY ./util/ ./util/
COPY ./metadata.py .
COPY ./tox.ini .
COPY ./setup.py .
COPY ./workers/ ./workers/

RUN pip install .
RUN ./scripts/install/workers.sh prod

RUN mkdir repos/;
COPY ./util/docker/docker.config.json .
RUN augur configure generate --rc-config-file docker.config.json

CMD augur run
