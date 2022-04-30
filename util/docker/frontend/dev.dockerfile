#SPDX-License-Identifier: MIT
FROM node:17

RUN DEBIAN_FRONTEND=noninteractive apt-get update -y && apt-get install -y \
    build-essential libcairo2-dev libpango1.0-dev libjpeg-dev libgif-dev librsvg2-dev

LABEL maintainer="outdoors@acm.org"
LABEL version="0.17.0"

WORKDIR /augur/frontend/
COPY ./util/docker/frontend/frontend.docker.config.json frontend.config.json
COPY frontend/package.json .
RUN yarn install --ignore-optional
COPY frontend/ .
CMD yarn dev