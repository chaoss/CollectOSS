FROM tiangolo/uwsgi-nginx-flask:python3.6

ENV STATIC_INDEX 0

COPY ./util/packaging/docker/augur/uwsgi.ini /app/uwsgi.ini
COPY ./util/packaging/docker/augur/prestart.sh /app/prestart.sh

WORKDIR /augur
ADD . .
RUN pip install -r requirements.txt

RUN augur configure generate --file util/packaging/docker/docker.config.json
RUN ./util/scripts/install/workers.sh
RUN mkdir repos/

EXPOSE 5000

CMD ["augur", "run"]