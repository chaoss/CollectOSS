FROM postgres:10

VOLUME /augur_data

ENV POSTGRES_PASSWORD "augur"
ENV POSTGRES_USER "augur"
ENV POSTGRES_DB "augur"

COPY ./persistence_schema/generate /docker-entrypoint-initdb.d/

EXPOSE 5432