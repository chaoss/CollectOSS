FROM rabbitmq:3.12-management-alpine

LABEL maintainer="574/augur@simplelogin.com"
LABEL version="0.62.2"

COPY --chown=rabbitmq:rabbitmq ./docker/rabbitmq/augur.conf /etc/rabbitmq/conf.d/

RUN chmod 777 /etc/rabbitmq/conf.d/augur.conf

RUN touch /etc/rabbitmq/advanced.config \
  && chmod 544 /etc/rabbitmq/advanced.config \
  && echo '[ {rabbit, [ {consumer_timeout, undefined} ]} ].' >> /etc/rabbitmq/advanced.config
