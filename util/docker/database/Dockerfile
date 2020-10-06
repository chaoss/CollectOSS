#SPDX-License-Identifier: MIT
FROM postgres:10 as setup-stage

LABEL maintainer="c@carterlandis.com"
LABEL version="0.1.0"

ENV POSTGRES_PASSWORD "augur"
ENV POSTGRES_USER "augur"
ENV POSTGRES_DB "augur"

FROM setup-stage as generate-schema

COPY ./schema/generate/ /docker-entrypoint-initdb.d/

EXPOSE 5432