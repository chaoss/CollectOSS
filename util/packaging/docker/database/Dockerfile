FROM postgres:10

ENV POSTGRES_PASSWORD "augur"
ENV POSTGRES_USER "augur"
ENV POSTGRES_DB "augur"

WORKDIR augur_data/

RUN rm -r /docker-entrypoint-initdb.d/*.*
COPY ./persistence_schema/generate/ /docker-entrypoint-initdb.d/

EXPOSE 5432
