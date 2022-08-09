#SPDX-License-Identifier: MIT
FROM node:16 as build-stage

LABEL maintainer="outdoors@acm.org"
LABEL version="0.27.8"

WORKDIR /augur/frontend/
COPY ./util/docker/frontend/frontend.docker.config.json frontend.config.json
# RUN cp frontend.docker.config.json frontend.config.json

FROM build-stage as core-ui
COPY frontend/package.json . 
COPY frontend/package-lock.json .
RUN npm install
RUN npx browserslist@latest --update-db
RUN npm install @vue/cli
COPY frontend/ .
RUN npm run build

# FROM build-stage as augurface
# WORKDIR /augur/augurface/
# COPY augurface/package.json .
# COPY augurface/package-lock.json .
# RUN npm install
# COPY augurface/ .
# RUN npm run build

FROM docker.io/library/nginx as production-stage
COPY --from=core-ui /augur/frontend/dist /usr/share/nginx/core
# COPY --from=augurface /augur/augurface/dist /usr/share/nginx/augurface
COPY ./util/docker/frontend/nginx.conf /etc/nginx/nginx.conf

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
