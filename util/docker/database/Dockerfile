#SPDX-License-Identifier: MIT
FROM postgres:12

LABEL maintainer="outdoors@acm.org"
LABEL version="0.27.8"

ENV POSTGRES_DB "test"
ENV POSTGRES_USER "augur"
ENV POSTGRES_PASSWORD "augur"

EXPOSE 5432

COPY ./schema/generate/01-schema.sql /docker-entrypoint-initdb.d/
COPY ./schema/generate/02-augur.sql /docker-entrypoint-initdb.d/
COPY ./schema/generate/05-seed_data.sql /docker-entrypoint-initdb.d/
