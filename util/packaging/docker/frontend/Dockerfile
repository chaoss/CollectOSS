FROM node:11 as build-stage

WORKDIR /augur_frontend

RUN touch augur.config.json
COPY ./util/packaging/docker/docker.config.json augur.config.json

COPY frontend/package*.json frontend/
WORKDIR frontend/
RUN npm install
RUN npm install -g @vue/cli
COPY frontend/ .

EXPOSE 8080

CMD ["npm", "run", "serve"]


