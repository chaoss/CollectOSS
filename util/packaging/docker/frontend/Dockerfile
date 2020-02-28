FROM node:11 as build-stage

WORKDIR augur_frontend/
COPY ./util/packaging/docker/frontend/frontend.config.json .
RUN cp frontend.config.json augur.config.json

WORKDIR frontend/
COPY frontend/package.json .
COPY frontend/package-lock.json .
RUN npm install
RUN npm install @vue/cli
COPY frontend/ .
RUN npm run build

FROM nginx as production-stage
COPY --from=build-stage /augur_frontend/frontend/dist /usr/share/nginx/html
COPY ./util/packaging/docker/frontend/nginx.conf /etc/nginx/nginx.conf

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]


# CMD ["npm", "run", "serve"]