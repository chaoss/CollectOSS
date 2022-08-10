#SPDX-License-Identifier: MIT
FROM node:16 as build-stage

LABEL maintainer="outdoors@acm.org"
LABEL version="0.42.0"

WORKDIR /augur/frontend/
COPY ./docker/frontend/docker.config.json frontend.config.json
# RUN cp frontend.docker.config.json frontend.config.json

FROM build-stage as core-ui
COPY frontend/package.json . 
COPY frontend/package-lock.json .
RUN npm install
RUN npx browserslist@latest --update-db
RUN npm install @vue/cli
COPY frontend/ .
RUN npm run build

FROM docker.io/library/nginx as production-stage
COPY --from=core-ui /augur/frontend/dist /usr/share/nginx/core
COPY ./docker/frontend/nginx.conf /etc/nginx/nginx.conf

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
