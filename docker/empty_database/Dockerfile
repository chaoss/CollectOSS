from postgres:16 AS builder

RUN apt-get update && \
    apt-get install -y gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

ENV DEBIAN_FRONTEND=noninteractive

# Install uv (https://docs.astral.sh/uv/guides/integration/docker/#installing-uv)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1
# The uv package cache will be on a cache volume, so can't be linked
ENV UV_LINK_MODE=copy
# Assert that the lockfile (uv.lock) is up-to-date. Use `uv lock` to update it
# manually if this fails the container build.
ENV UV_LOCKED=1

WORKDIR /augur

COPY pyproject.toml .
COPY uv.lock .
COPY .python-version .

# Install augur's dependencies early to take advantage of build cache
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-install-project --no-dev

# Copy in the actual code
# The RUN line below ensure that permissions are set correctly.
# This is the equivalent of the following docker --chmod flags, but done in a way thats compatible with podman.
# This can be removed once https://github.com/containers/buildah/issues/6066 or relevant equivalent is fixed
# - u=rw,u+X: user can read and write all files/dirs and execute directories
# - go=r,go+X: group and others can read all files/dirs and execute directories
COPY README.md .
COPY LICENSE .
COPY alembic.ini .
COPY augur/ augur/
COPY metadata.py .
COPY scripts/ scripts/

RUN find augur -type d -exec chmod u=rwx,go=rx {} + && find augur -type f -exec chmod u=rw,go=r {} +

RUN find scripts -exec chmod u=rwx,go=rx {} +

# Install the main project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev

# We aren't going to activate the virtualenv (manually or via uv run), so we
# need adjust the PATH
ENV PATH="/augur/.venv/bin:${PATH}"

ENV POSTGRES_DB="augur"
ENV POSTGRES_USER="augur"
ENV POSTGRES_PASSWORD="augur"
ENV AUGUR_DB="postgresql+psycopg2://augur:augur@localhost:5432/augur"
# ENV PGDATA="/var/lib/postgresql/data"

RUN set -e && \
    gosu postgres initdb && \
    gosu postgres pg_ctl -D "$PGDATA" -o "-c listen_addresses='localhost'" -w start && \
    gosu postgres psql -c "CREATE USER ${POSTGRES_USER} WITH SUPERUSER PASSWORD '${POSTGRES_PASSWORD}';" && \
    gosu postgres psql -c "CREATE DATABASE ${POSTGRES_DB} OWNER ${POSTGRES_USER};" && \
    augur db create-schema && \
    gosu postgres pg_ctl -D "$PGDATA" -m fast -w stop


FROM postgres:16

COPY --from=builder /var/lib/postgresql/data /var/lib/postgresql/data
