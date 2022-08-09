#SPDX-License-Identifier: MIT
FROM node:16 as build-stage

LABEL maintainer="outdoors@acm.org"
LABEL version="0.27.8"

WORKDIR /augur/frontend/
COPY ./util/docker/frontend/frontend.docker.config.json frontend.config.json

FROM build-stage as augurface
WORKDIR /augur/augurface/
COPY augurface/package.json .
COPY augurface/package-lock.json .
RUN npm install
RUN npm install @vue/cli
COPY augurface/ .
RUN npx browserslist@latest --update-db
RUN npm run build

FROM nginx as production-stage
COPY --from=augurface /augur/augurface/dist /usr/share/nginx/augurface
COPY ./util/docker/augurface/nginx.conf /etc/nginx/nginx.conf

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
