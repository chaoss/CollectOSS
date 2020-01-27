FROM postgres:10

RUN rm -rf /augur_data
RUN mkdir /augur_data

ENV POSTGRES_PASSWORD "password"
ENV POSTGRES_USER "augur"
ENV POSTGRES_DB "augur"
ENV POSTGRES_DB "augur"

COPY ./persistence_schema/generate /docker-entrypoint-initdb.d/
