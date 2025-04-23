# SPDX-License-Identifier: MIT


########################################
FROM golang:1.23 AS golang-builder

# Write final binaries to / so it's easy to copy them out
ENV GOBIN=/

RUN go install github.com/boyter/scc/v3@v3.4.0 \
    && /scc --version
RUN go install github.com/ossf/scorecard/v5@v5.1.1 \
    && /scorecard version


########################################
FROM python:3.11-slim-bullseye

LABEL maintainer="outdoors@acm.org"
LABEL version="0.86.0"

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
        chromium \
        tar \
	jq \
        chromium-driver \
        && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Firefox from Debian repositories for ARM64 architecture
RUN set -x \
    && apt-get update \
    && apt-get install -y firefox-esr

# Install Geckodriver
RUN GECKODRIVER_VERSION=$(curl -s https://api.github.com/repos/mozilla/geckodriver/releases/latest | jq -r '.tag_name' | sed 's/v//') \
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





EXPOSE 5000

WORKDIR /augur
COPY --chmod=u=rw,u+X,go=r,go+X ./README.md .
COPY --chmod=u=rw,u+X,go=r,go+X ./alembic.ini .
COPY --chmod=u=rw,u+X,go=r,go+X ./augur/ augur/
COPY --chmod=u=rw,u+X,go=r,go+X ./metadata.py .
COPY --chmod=u=rw,u+X,go=r,go+X ./setup.py .
COPY --chmod=u=rw,u+X,go=r,go+X ./scripts/ scripts/
COPY --chmod=u=rw,u+X,go=r,go+X ./keyman/ keyman/

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

ENV SCC_DIR=/scc
COPY --from=golang-builder --chmod=u=rw,u+X,go=r,go+X "/scc" "/scc/scc"
ENV SCORECARD_DIR=/scorecard
COPY --from=golang-builder --chmod=u=rw,u+X,go=r,go+X "/scorecard" "/scorecard/scorecard"

RUN mkdir -p repos/ logs/ /augur/facade/

COPY --chmod=u=rwx,go=rx ./docker/backend/entrypoint.sh /
COPY --chmod=u=rwx,go=rx ./docker/backend/init.sh /
ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]
CMD ["/init.sh"]
