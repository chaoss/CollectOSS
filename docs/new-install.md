## Augur Setup
### Docker
1. Make sure docker, and docker-compose are both installed
2. Modify the `environment.txt` file in the root of the repository to include your GitHub and GitLab API keys.
3. If you are already running postgresql on your server you have two choices: 
   - Change the port mappings in the `docker-compose.yml` file to match ports for Postgresql not currently in use.
   - Change to variables in `environment.txt` to include the correct values for your local, non-docker-container database.
4. `sudo docker build -t augur-new -f docker/backend/Dockerfile .`
5. `sudo docker-compose --env-file ./environment.txt --file docker-compose.yml up` to run the database in a Docker Container or 
   `sudo docker-compose --env-file ./environment.txt --file docker-compose.yml up` to connect to an already running database. 
### Regular Installation
0. Follow the installation instructions for the database here: https://oss-augur.readthedocs.io/en/main/quick-start.html#postgresql-installation
0. 
1. Clone Augur, or clone your fork of Augur if you wish to make contributions
2. Install `redis-server` at the operating system level
3. Make sure you have `Go` version is 1.19.3. If you don't know how to install `Go`, instructions are provided during the installation process.
4. Create a Python Virtual Environment `python3 -m venv ~/virtual-env-directory`
5. Activate your Python Virtual Environment `source ~/virtual-env-directory/bin/activate`
6. From the root of the Augur Directory, type `make install`
7. You will be prompted to provide your GitHub username and password, your GitLab username and password, and the postgresql database where you want to have the Augur Schema built. You will also be prompted to provide a directory where repositories will be clone into. 
8. To access command line options, use `augur --help`. To load repos from GitHub organizations prior to collection, or in other ways, the direct route is `augur db --help`. 
9. Start a Flower Dashboard, which you can use to monitor progress, and report any failed processes as issues on the Augur GitHub site. The error rate for tasks is currently 0.04%, and most errors involve unhandled platform API timeouts. We continue to identify and add fixes to handle these errors through additional retries. Starting Flower: `(nohup celery -A augur.tasks.init.celery_app.celery_app flower --port=8400 --max-tasks=1000000 &)` NOTE: You can use any open port on your server, and access the dashboard in a browser with http://servername-or-ip:8400 in the example above (assuming you have access to that port, and its open on your network.)
10. Start Augur: `(nohup augur backend start &)`
11. When data collection is complete you will see only a single task running in your flower Dashboard.
12. You can stop augur with `augur backend stop`, followed by `augur backend kill`. We recommend waiting 5 minutes between commands so Augur can shutdown more gently. There is no issue with data integrity if you issue them seconds apart, its just that stopping is nicer than killing. 
13. If you wish to run the frontend, create a file called `frontend/frontend.config.json following this structure, with relevant values`: (Default port is 5000. This can be changed in the `augur_operations.config` table.). Then run `npm install` and `npm run build` in the frontend directory. `npm run serve will make a development server (usually on your local machine)` version of the frontend available. If you wish to run Augur's frontend through nginx, you can follow these instructions here: https://oss-augur.readthedocs.io/en/augur-new/deployment/nginx-configuration.html?highlight=nginx#nginx and here: https://oss-augur.readthedocs.io/en/augur-new/deployment/nginx-configuration.html?highlight=nginx#site-configuration 
NOTE: `"host": "your resolvable server"`
    ```json
    {
        "Frontend": {
            "host": "chaoss.tv",
            "port": 5000,
            "ssl": false
        },
        "Server": {
            "cache_expire": "3600",
            "host": "0.0.0.0",
            "port": 5000,
            "workers": 6,
            "timeout": 6000,
            "ssl": false,
            "ssl_cert_file": null,
            "ssl_key_file": null
        }
    }
    ```
14. If you have frontend configuration issues that result in a *failure* to complete steps with npm, we recommend you install and use `nvm`: https://tecadmin.net/how-to-install-nvm-on-ubuntu-20-04/ to set your nodejs release to the latest LTS of 12.x or 16.x. For example: `nvm ls-remote | grep -i 'latest'` and `nvm alias default 16.??` (whatever the latest version of 16 is.)
15. Also, please explore our new frontend, being developed at https://github.com/augurlabs/augur_view. The `dev` branch is the most current. 
