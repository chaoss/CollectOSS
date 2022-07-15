#SPDX-License-Identifier: MIT
FROM python:3.8.11-slim-buster

LABEL maintainer="outdoors@acm.org"
LABEL version="0.27.4"

ENV DEBIAN_FRONTEND=noninteractive

RUN set -x \
    && apt-get update \
    && apt-get -y install --no-install-recommends \
        git \
        gcc \
        python3-pip \
        wget \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 5000

WORKDIR /augur

COPY ./scripts/docker/install-go.sh ./scripts/docker/install-go.sh
RUN ./scripts/docker/install-go.sh && pip install -U pip

COPY ./scripts/install/workers.sh ./scripts/install/workers.sh
COPY ./workers/ workers/
RUN ./scripts/install/workers.sh

COPY ./README.md .
COPY ./augur/ augur/
COPY ./metadata.py .
COPY ./setup.py .
RUN set -x && pip install .

COPY ./scripts/ scripts/
COPY ./schema/ schema/
COPY ./util/docker/backend/entrypoint.sh ./util/docker/backend/entrypoint.sh
COPY ./util/docker/backend/backend.docker.config.json .

<<<<<<< HEAD
RUN mkdir -p repos/ logs/ &&\
    chmod +x ./util/docker/backend/entrypoint.sh &&\
    augur config init --rc-config-file /augur/backend.docker.config.json
=======
RUN set -x \
    && pip install .

RUN ./scripts/docker/install-go.sh
RUN ./scripts/install/workers.sh 
RUN augur config init --rc-config-file /augur/backend.docker.config.json \
    && mkdir -p repos/ logs/
>>>>>>> augur-new

ENTRYPOINT /augur/util/docker/backend/entrypoint.sh
