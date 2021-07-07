#SPDX-License-Identifier: MIT
FROM postgres:12

LABEL maintainer="outdoors@acm.org"
LABEL version="0.15.4"

ENV POSTGRES_DB "augur"
ENV POSTGRES_USER "augur"
ENV POSTGRES_PASSWORD "augur"

EXPOSE 5432

COPY ./schema/generate/ /docker-entrypoint-initdb.d/
