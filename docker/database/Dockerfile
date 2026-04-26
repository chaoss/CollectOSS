#SPDX-License-Identifier: MIT
FROM postgres:16

LABEL org.opencontainers.image.authors="CHAOSS https://chaoss.community"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.source="https://github.com/chaoss/collectoss"
LABEL org.opencontainers.image.documentation="https://collectoss.readthedocs.io"

ARG VERSION
LABEL org.opencontainers.image.version=${VERSION}

ENV POSTGRES_DB="test"
ENV POSTGRES_USER="augur"
ENV POSTGRES_PASSWORD="augur"

EXPOSE 5432

COPY ./docker/database/collectoss-new-schema.sql /docker-entrypoint-initdb.d/
