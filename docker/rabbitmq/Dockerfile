FROM rabbitmq:4.1-management-alpine

LABEL org.opencontainers.image.authors="CHAOSS https://chaoss.community"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.source="https://github.com/chaoss/collectoss"
LABEL org.opencontainers.image.documentation="https://docs.collectoss.org"

ARG VERSION
LABEL org.opencontainers.image.version=${VERSION}

COPY --chown=rabbitmq:rabbitmq ./docker/rabbitmq/collectoss.conf /etc/rabbitmq/conf.d/

COPY --chown=rabbitmq:rabbitmq docker/rabbitmq/definitions.json /etc/rabbitmq/

ADD docker/rabbitmq/advanced.config /etc/rabbitmq/
RUN chown rabbitmq:rabbitmq /etc/rabbitmq/advanced.config

RUN chmod 777 /etc/rabbitmq/conf.d/collectoss.conf

RUN apk add --no-cache python3
COPY docker/rabbitmq/update_config.py /
COPY docker/rabbitmq/docker-entrypoint.sh /collectoss-rabbitmq-entrypoint.sh

ENTRYPOINT ["/bin/sh", "/collectoss-rabbitmq-entrypoint.sh"]
CMD ["rabbitmq-server"]
