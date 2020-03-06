FROM augurlabs/augur:database

LABEL maintainer="c@carterlandis.com"
LABEL version="0.1.0"

COPY ./schema/sample_data/load_sample_data.sql /docker-entrypoint-initdb.d/
COPY ./schema/sample_data/*.txt schema/sample_data/

EXPOSE 5432