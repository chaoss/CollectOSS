# SPDX-License-Identifier: MIT


########################################
FROM golang:1.23 AS golang-builder

# Write final binaries to / so it's easy to copy them out
ENV GOBIN=/
# Disable CGO to ensure the binaries are statically linked
# Discussion: https://github.com/chaoss/augur/pull/3142
ENV CGO_ENABLED=0

RUN go install github.com/boyter/scc/v3@v3.4.0 \
    && /scc --version
RUN go install github.com/ossf/scorecard/v5@v5.1.1 \
    && /scorecard version


########################################
FROM python:3.11-slim-bullseye

LABEL maintainer="outdoors@acm.org"
LABEL version="0.86.1"

ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="/usr/bin/:/usr/local/bin:/usr/lib:${PATH}"

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
        wget \
        postgresql-client \
        libpq-dev \
        build-essential \
        chromium \
        tar \
        jq \
        chromium-driver \
        firefox-esr \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

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

# Install uv (https://docs.astral.sh/uv/guides/integration/docker/#installing-uv)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1
# The uv package cache will be on a cache volume, so can't be linked
ENV UV_LINK_MODE=copy
# Assert that the lockfile (uv.lock) is up-to-date. Use `uv lock` to update it
# manually if this fails the container build.
ENV UV_LOCKED=1

WORKDIR /augur

# Install augur's dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=.python-version,target=.python-version \
    uv sync --no-install-project --no-dev

# Copy in the actual code
# The --chmod flags ensure that permissions are set correctly:
# - u=rw,u+X: user can read and write all files/dirs and execute directories
# - go=r,go+X: group and others can read all files/dirs and execute directories
COPY --chmod=u=rw,u+X,go=r,go+X pyproject.toml .
COPY --chmod=u=rw,u+X,go=r,go+X uv.lock .
COPY --chmod=u=rw,u+X,go=r,go+X .python-version .
COPY --chmod=u=rw,u+X,go=r,go+X README.md .
COPY --chmod=u=rw,u+X,go=r,go+X LICENSE .
COPY --chmod=u=rw,u+X,go=r,go+X alembic.ini .
COPY --chmod=u=rw,u+X,go=r,go+X augur/ augur/
COPY --chmod=u=rw,u+X,go=r,go+X metadata.py .
COPY --chmod=u=rw,u+X,go=r,go+X scripts/ scripts/
COPY --chmod=u=rw,u+X,go=r,go+X keyman/ keyman/

# Install the main project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev

# We aren't going to activate the virtualenv (manually or via uv run), so we
# need adjust the PATH
ENV PATH="/augur/.venv/bin:${PATH}"

ENV SCC_DIR=/scc
COPY --from=golang-builder --chmod=u=rw,u+X,go=r,go+X "/scc" "/scc/scc"
ENV SCORECARD_DIR=/scorecard
COPY --from=golang-builder --chmod=u=rw,u+X,go=r,go+X "/scorecard" "/scorecard/scorecard"
# Verify installations
RUN ${SCC_DIR}/scc --version
RUN ${SCORECARD_DIR}/scorecard version

RUN mkdir -p repos/ logs/ /augur/facade/
RUN ln -s /cache /augur/augur/static/cache

# Copy in the entrypoint and init scripts, ensuring they are executable
COPY --chmod=u=rwx,go=rx ./docker/backend/entrypoint.sh /
COPY --chmod=u=rwx,go=rx ./docker/backend/init.sh /
RUN chmod +x /entrypoint.sh /init.sh
ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]
CMD ["/init.sh"]
