FROM node:11

WORKDIR /augur_frontend
COPY . /augur_frontend

RUN touch augur.config.json
RUN cp ./util/packaging/docker/frontend/frontend.config.json augur.config.json

EXPOSE 8080

WORKDIR frontend/
ENTRYPOINT ["npm", "run", "start"]


