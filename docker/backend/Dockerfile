#SPDX-License-Identifier: MIT
ARG target

FROM python:3.10-bullseye AS base

LABEL maintainer="outdoors@acm.org"
LABEL version="0.51.1"

ENV DEBIAN_FRONTEND=noninteractive

RUN set -x \
    && apt-get update \
    && apt-get -y install --no-install-recommends \
        git \
        bash \
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

RUN ./scripts/docker/install-workers-deps.sh

RUN ./scripts/docker/install-go.sh
# RUN ./scripts/install/workers.sh 

RUN mkdir -p repos/ logs/ /augur/facade/

FROM base AS install-default
COPY ./docker/backend/entrypoint.sh /
RUN chmod +x /entrypoint.sh
ENTRYPOINT /entrypoint.sh

FROM base AS install-graphical
COPY ./docker/backend/graphical.sh /
RUN chmod +x /graphical.sh
ENTRYPOINT /graphical