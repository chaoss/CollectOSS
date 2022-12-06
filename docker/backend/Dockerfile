#SPDX-License-Identifier: MIT
FROM python:3.8.11-slim-buster

LABEL maintainer="outdoors@acm.org"
LABEL version="0.42.0"

ENV DEBIAN_FRONTEND=noninteractive

RUN set -x \
    && apt-get update \
    && apt-get -y install --no-install-recommends \
        git \
        curl \
        gcc \
        python3-pip \
        wget \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 5000

WORKDIR /augur
COPY ./README.md .
COPY ./alembic.ini .
COPY ./augur/ augur/
COPY ./metadata.py .
COPY ./setup.py .
COPY ./scripts/ scripts/

#COPY ./docker/backend/docker.config.json .
RUN python3 -m venv /opt/venv

RUN set -x \
    && /opt/venv/bin/pip install .

RUN ./scripts/docker/install-go.sh
# RUN ./scripts/install/workers.sh 

RUN mkdir -p repos/ logs/ /augur/facade/

COPY ./docker/backend/entrypoint.sh /
RUN chmod +x /entrypoint.sh
ENTRYPOINT /entrypoint.sh
