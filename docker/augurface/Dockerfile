#SPDX-License-Identifier: MIT
FROM node:16 as build-stage

LABEL maintainer="outdoors@acm.org"
LABEL version="0.42.0"

WORKDIR /augur/frontend/
COPY ./docker/frontend/docker.config.json frontend.config.json

FROM build-stage as augurface
WORKDIR /augur/augur/augurface/
COPY augur/augurface/package.json .
COPY augur/augurface/package-lock.json .
RUN npm install
RUN npm install @vue/cli
COPY augur/augurface/ .
RUN npx browserslist@latest --update-db
RUN npm run build

FROM nginx as production-stage
COPY --from=augurface /augur/augur/augurface/dist /usr/share/nginx/augurface
COPY ./docker/augurface/nginx.conf /etc/nginx/nginx.conf

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
