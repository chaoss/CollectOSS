FROM tiangolo/uwsgi-nginx-flask:python3.6

ENV STATIC_INDEX 0

COPY ./util/packaging/docker/uwsgi.ini /app/uwsgi.ini
COPY ./util/packaging/docker/prestart.sh /app/prestart.sh

RUN mkdir /augur
WORKDIR /augur
ADD . /augur
RUN pip install --upgrade .