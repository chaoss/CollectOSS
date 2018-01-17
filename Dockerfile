FROM python:3

FROM tiangolo/uwsgi-nginx-flask:python3.6

ENV STATIC_INDEX 1

COPY ./docker/uwsgi.ini /app/uwsgi.ini
COPY ./frontend/public /app/static

RUN mkdir /ghdata
WORKDIR /ghdata
ADD . /ghdata
RUN pip install --upgrade .