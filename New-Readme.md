# New Front End Stuff Figuring Out

# Augur Install Steps

# Start back end
1. verify augur.config.json components (note the server port (5002 in this case), as its referred to later in the nginx configuration)
```
        {
            "Cache": {
                "config": {
                    "cache.data_dir": "runtime/cache/",
                    "cache.lock_dir": "runtime/cache/",
                    "cache.type": "file"
                }
            },
            "Database": {
                "connection_string": "sqlite:///:memory:",
                "database": "augur_twitter_test",
            "name": "augur_twitter_test",
                "host": "localhost",
                "password": "xxxxxx",
                "port": "xxxxx",
                "schema": "xxxxxx",
                "user": "auxxxgur",
                "key": "xxxxxx",
                "zombie_id": "22"
            },
            "Development": {
                "developer": "0",
                "interactive": "0"
            },
            "Facade": {
                "host": "opendata.missouri.edu",
                "name": "facade",
                "pass": "xxxxx",
                "port": "3306",
                "projects":["xxxxx"],
                "user": "facade"
            },
            "GHTorrent": {
                "host": "localhost",
                "name": "ghtorrent_restore",
                "pass": "xxxx!",
                "port": "xxxxx",
                "user": "xxxx"
            },
            "GHTorrentPlus": {
                "host": "augurlabs.io",
                "name": "xxx",
                "pass": "xxxx",
                "port": "xxx",
                "user": "xxx"
            },
            "GitHub": {
                "apikey": "xxxxxx"
            },
            "LibrariesIO": {
                "apikey": "None",
                "host": "xxxxx.io",
                "name": "xxxxx.io",
                "pass": "xxxxx!",
                "port": "3306",
                "user": "xxxx"
            },
            "Plugins": [],
            "Postman": {
                "apikey": "xxxxxx"
            },
            "Plugins": [],
            "PublicWWW": {
                "apikey": "xxxxx"
            },
            "Server": {
                "cache_expire": 3600,
                "host": "0.0.0.0",
                "port": "5002",
                "workers": 8
            },
            "Controller": {
              "broker": 1,
              "github_worker": 0,
              "housekeeper": 1
            },
            "Housekeeper": {
              "jobs": [
                    {
                        "model": "issues",
                        "delay": 345000,
                        "repo_group_id": 0 
                    }
                ]
            },
            "GitHubWorker": {
                "port": 51238,
                "workers": 1
            }    
        }

```
2. `nohup augur run >> augur.log 2 >> augur.err &`

# Start Back End for Development
1. `cd frontend`
2. `npm install`
3. To start a development Server: `npm run serve`. This will let you see the emerging front end on local host.  

# Start Backend on an NGINX Server (in development)
1. Unknown right now: How do we get the API from the back end communicating with the front end? 
2. Current Hack: 
    - API is running at http://newtwittertest.augurlabs.io/api/unstable as usual, using nginx with this config: 
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