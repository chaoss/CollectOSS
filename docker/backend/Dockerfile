#SPDX-License-Identifier: MIT
FROM python:3.10-bookworm

LABEL maintainer="outdoors@acm.org"
LABEL version="0.76.1"

ENV DEBIAN_FRONTEND=noninteractive

RUN set -x \
    && apt-get update \
    && apt-get -y install --no-install-recommends \
        git \
        bash \
        curl \
        gcc \
        software-properties-common \
        postgresql-contrib \
        musl-dev \
        python3-dev \
        python3-distutils \
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
    && /opt/venv/bin/pip install --upgrade pip 

RUN set -x \
    && /opt/venv/bin/pip install wheel
    
RUN set -x \
    && /opt/venv/bin/pip install .
    
RUN set -x \
    && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install wheel \
    && /opt/venv/bin/pip install .

RUN ./scripts/docker/install-workers-deps.sh

RUN ./scripts/docker/install-go.sh
# RUN ./scripts/install/workers.sh 

RUN mkdir -p repos/ logs/ /augur/facade/

COPY ./docker/backend/entrypoint.sh /
COPY ./docker/backend/init.sh /
RUN chmod +x /entrypoint.sh /init.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD /init.sh
