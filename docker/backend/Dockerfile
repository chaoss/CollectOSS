# SPDX-License-Identifier: MIT
FROM python:3.12-bookworm

LABEL maintainer="outdoors@acm.org"
LABEL version="0.76.1"

ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="/usr/bin/:/usr/local/bin:/usr/lib:${PATH}"

RUN set -x \
    && apt-get update \
    && apt-get -y install \
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

# Install Firefox from Debian repositories for ARM64 architecture
RUN set -x \
    && apt-get update \
    && apt-get install -y firefox-esr

# Install Geckodriver
RUN GECKODRIVER_VERSION=$(curl -s https://api.github.com/repos/mozilla/geckodriver/releases/latest | grep 'tag_name' | cut -d\" -f4 | sed 's/v//') \
    && ARCH=$(uname -m) \
    && if [ "$ARCH" = "aarch64" ]; then \
         GECKODRIVER_URL="https://github.com/mozilla/geckodriver/releases/download/v${GECKODRIVER_VERSION}/geckodriver-v${GECKODRIVER_VERSION}-linux-aarch64.tar.gz"; \
         GECKODRIVER_FILE="geckodriver-v${GECKODRIVER_VERSION}-linux-aarch64.tar.gz"; \
       else \
         GECKODRIVER_URL="https://github.com/mozilla/geckodriver/releases/download/v${GECKODRIVER_VERSION}/geckodriver-v${GECKODRIVER_VERSION}-linux64.tar.gz"; \
         GECKODRIVER_FILE="geckodriver-v${GECKODRIVER_VERSION}-linux64.tar.gz"; \
       fi \
    && wget $GECKODRIVER_URL \
    && tar -xzf $GECKODRIVER_FILE \
    && mv geckodriver /usr/local/bin/ \
    && rm $GECKODRIVER_FILE

# Verify installations
RUN firefox --version
RUN geckodriver --version

# Ensure Rust directories are writable
RUN mkdir -p /root/.rustup/downloads /root/.cargo/registry && \
    chmod -R 777 /root/.rustup /root/.cargo

# Add rust and cargo to PATH
ENV PATH="/root/.cargo/bin:${PATH}"

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

# Add rust and cargo to PATH
ENV PATH="/usr/bin/:/root/.cargo/bin:/usr/local/bin:${PATH}"

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
ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]
#ENTRYPOINT ["/entrypoint.sh"]
CMD /init.sh