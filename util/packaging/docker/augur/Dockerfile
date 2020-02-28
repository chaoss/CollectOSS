FROM tiangolo/uwsgi-nginx-flask:python3.6 as build-stage

LABEL maintainer="c@carterlandis.com"
LABEL version="0.1.0"

ENV STATIC_INDEX 0
COPY ./util/packaging/docker/augur/uwsgi.ini /app/uwsgi.ini
COPY ./util/packaging/docker/augur/prestart.sh /app/prestart.sh

WORKDIR /augur
COPY . .

RUN rm -rf frontend/
RUN rm -rf schema/

RUN pip install -r requirements.txt

EXPOSE 5000

FROM build-stage as worker-stage
RUN ./util/scripts/install/workers.sh
RUN mkdir repos/

FROM worker-stage as production-stage
RUN augur configure generate --rc-config-file ./util/packaging/docker/docker.config.json

CMD augur run