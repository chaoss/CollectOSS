### Start Front End on an NGINX Server (Mostly useful if you are installing on a remote server.)
1. Current State: We are updating how our front end communicates with our back end. If you want to delv into nginx, which is probably not necessary right now, there are a couple of "hacks". 
2. Current Hack: 
    - Example: Our API is running at http://newtwittertest.augurlabs.io/api/unstable as usual, using nginx with this config: 
```
        server {
            server_name newtwittertest.augurlabs.io;

            location / {
                proxy_pass http://localhost:5002/;
                proxy_set_header Host $host;
            }
        }

```
    - `cd frontend`
    - `yarn build`
    - Create a new subdomain for the frontend. Currently this is http://vue-cli.augurlabs.io
    - NGINX Config in `/etc/nginx/sites-enabled/vue-cli.augurlabs.io`
```
        server {
            listen      80;
            server_name vue-cli.augurlabs.io;    charset utf-8;
            root     /home/sean/github/augur-twitter-test/frontend/dist;
            index   index.html index.htm;    # Always serve index.html for any request
            location / {
                root  /home/sean/github/augur-twitter-test/frontend/dist; 
                try_files $uri /index.html;
            }    error_log  /var/log/nginx/vue-app-error.log;
            access_log /var/log/nginx/vue-app-access.log;
        }

```

3. Alt-Hack: Open port 8080 and run `npm serve` as in dev 
    - `sudo ufw status verbose` (make sure port 8080 is open)
    - If its not open: `sudo ufw allow 8080/tcp` 
    - In this case you don't need the additional domain name. 