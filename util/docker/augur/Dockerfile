FROM python:3.6-slim-buster as build-stage

COPY ./util/docker/augur/install_packages.sh .
RUN ./install_packages.sh

LABEL maintainer="c@carterlandis.com"
LABEL version="0.1.0"

WORKDIR /augur

# setup.py requires the README.md for the description 
COPY ./README.md . 

COPY ./requirements.txt .
COPY ./setup.py .
COPY ./augur/ ./augur/
RUN pip install .

RUN mkdir repos/;
COPY ./workers/ ./workers/
COPY ./scripts/install/workers.sh .

COPY ./util/docker/docker.config.json .
RUN augur configure generate --rc-config-file docker.config.json
RUN ./workers.sh

CMD augur run --disable-housekeeper
