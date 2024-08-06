#SPDX-License-Identifier: MIT
FROM python:3.12-bookworm

LABEL maintainer="outdoors@acm.org"
LABEL version="0.76.1"

ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="/usr/bin/:/usr/local/bin:/usr/lib:${PATH}"

RUN set -x \
    && apt-get update \
    && apt-get -y install \
     # --no-install-recommends \
        git \
        bash \
        curl \
        gcc \
        software-properties-common \
        postgresql-contrib \
        musl-dev \
        python3-dev \
        python3-distutils \
        python3-venv \ 
        wget \
        postgresql-client \
        libpq-dev \
        build-essential \
        rustc \ 
        cargo \ 
        chromium \
        chromium-driver \
        && apt-get clean \ 
    && rm -rf /var/lib/apt/lists/* \
    && curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

# Add rust and cargo to PATH
ENV PATH="/root/.cargo/bin:${PATH}"

# Ensure enough disk space and clean previous installations
RUN set -x \ 
    rustup self update

# Ensure Rust directories are writable
RUN mkdir -p /root/.rustup/downloads /root/.cargo/registry && \
    chmod -R 777 /root/.rustup /root/.cargo

# Install the specific version of Rust
RUN set -x \ 
    && rustup install 1.78.0
RUN set -x \ 
    && rustup default 1.78.0


EXPOSE 5000

WORKDIR /augur
COPY ./README.md .
COPY ./alembic.ini .
COPY ./augur/ augur/
COPY ./metadata.py .
COPY ./setup.py .
COPY ./scripts/ scripts/

# Install GeckoDriver for Visualization 
RUN set -x \ 
    && cargo install geckodriver  --force

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
