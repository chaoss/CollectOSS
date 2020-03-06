FROM postgres:10

LABEL maintainer="c@carterlandis.com"
LABEL version="0.1.0"

ENV POSTGRES_PASSWORD "augur"
ENV POSTGRES_USER "augur"
ENV POSTGRES_DB "augur"

COPY ./schema/generate/ /docker-entrypoint-initdb.d/

EXPOSE 5432