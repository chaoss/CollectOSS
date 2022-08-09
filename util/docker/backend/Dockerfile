#SPDX-License-Identifier: MIT
FROM python:3.8.11-slim-buster

LABEL maintainer="outdoors@acm.org"
LABEL version="0.27.8"

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
COPY ./README.md .
COPY ./augur/ augur/
COPY ./metadata.py .
COPY ./setup.py .
COPY ./scripts/ scripts/
COPY ./workers/ workers/
COPY ./schema/ schema/

COPY ./util/docker/backend/backend.docker.config.json .

RUN set -x \
    && pip install .

RUN ./scripts/docker/install-go.sh
RUN ./scripts/install/workers.sh 
RUN augur config init --rc-config-file /augur/backend.docker.config.json \
    && mkdir -p repos/ logs/

COPY ./util/docker/backend/entrypoint.sh /
RUN chmod +x /entrypoint.sh
ENTRYPOINT /entrypoint.sh
