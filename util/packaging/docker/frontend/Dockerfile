FROM node:11 as build-stage


WORKDIR augur_frontend/
COPY ./util/packaging/docker/frontend/frontend.config.json .
RUN cp frontend.config.json augur.config.json

WORKDIR frontend/
COPY frontend/package*.json .
RUN npm install
RUN npm install @vue/cli
RUN npm audit fix
COPY frontend/ .

RUN pwd > echo.txt
RUN cat echo.txt
RUN ls > echo.txt
RUN cat echo.txt

EXPOSE 8080


CMD ["npm", "run", "serve"]
