FROM rabbitmq:4.1-management-alpine

LABEL org.opencontainers.image.authors="CHAOSS https://chaoss.community"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.source="https://github.com/chaoss/collectoss"
LABEL org.opencontainers.image.documentation="https://collectoss.readthedocs.io"

ARG VERSION
LABEL org.opencontainers.image.version=${VERSION}

ARG RABBIT_MQ_DEFAULT_USER=collectoss
ARG RABBIT_MQ_DEFAULT_PASSWORD=password123
ARG RABBIT_MQ_DEFAULT_VHOST=collectoss_vhost

COPY --chown=rabbitmq:rabbitmq ./docker/rabbitmq/collectoss.conf /etc/rabbitmq/conf.d/

ADD docker/rabbitmq/definitions.json /etc/rabbitmq/

ADD docker/rabbitmq/advanced.config /etc/rabbitmq/
RUN chown rabbitmq:rabbitmq /etc/rabbitmq/advanced.config

RUN chmod 777 /etc/rabbitmq/conf.d/collectoss.conf

RUN apk add --no-cache python3
COPY docker/rabbitmq/update_config.py /

RUN exec python3 update_config.py

RUN chown rabbitmq:rabbitmq /etc/rabbitmq/definitions.json
