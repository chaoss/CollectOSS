## Augur Setup

# Ubuntu 20.04.x
We default to this version of Ubuntu for the moment because Augur does not yet support python3.10, which is the default version of python3.x distributed with Ubuntu 22.0x.x

## Git Platform Requirements (Things to have setup prior to initiating installation.)
1. Obtain a GitHub Access Token: https://github.com/settings/tokens
2. Obtain a GitLab Access Token: https://gitlab.com/-/profile/personal_access_tokens

### Fork and Clone Augur
1. Fork https://github.com/chaoss/augur 
2. Clone your fork. We recommend creating a `github` directory in your user's base directory. 

## Pre-Requisite Operating System Level Packages
Here we ensure your system is up to date, install required python libraries, install postgresql, and install our queuing infrastrucutre, which is composed of redis-server and rabbitmq-server

### Executable
```shell 
sudo apt update && 
sudo apt upgrade && 
sudo apt install software-properties-common && 
sudo apt install python3-dev && 
sudo apt install python3.8-venv &&
sudo apt install postgresql postgresql-contrib postgresql-client && 
sudo apt install build-essential && 
sudo apt install redis-server &&  
sudo apt install erlang && 
sudo apt install rabbitmq-server && 
sudo snap install go --classic && 
sudo apt install nginx && 
sudo apt install firefox-geckodriver
```

### Annotated
```shell 
sudo apt update && 
sudo apt upgrade && 
sudo apt install software-properties-common && 
sudo apt install python3-dev && 
sudo apt install python3.8-venv &&
sudo apt install postgresql postgresql-contrib postgresql-client && 
sudo apt install build-essential && 
sudo apt install redis-server &&  # required 
sudo apt install erlang && # required
sudo apt install rabbitmq-server && #required
sudo snap install go --classic && #required: Go Needs to be version 1.19.x or higher. Snap is the package manager that gets you to the right version. Classic enables it to actually be installed at the correct version.
sudo apt install nginx && # required for hosting
sudo apt install firefox-geckodriver # required for visualization API 
```

## Git Configuration
There are some Git configuration parameters that help when you are cloning repos over time, and a platform prompts you for credentials when it finds a repo is deleted:
```shell 
    git config --global diff.renames true
    git config --global diff.renameLimit 200000
    git config --global credential.helper cache
    git config --global credential.helper 'cache --timeout=9999999999999'
```


## Postgresql Configuration
Create a PostgreSQL database for Augur to use
```shell
sudo su -
su - postgres
psql
```

Then, from within the resulting postgresql shell: 
```sql
CREATE DATABASE augur;
CREATE USER augur WITH ENCRYPTED PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE augur TO augur;
```

Once you are successfully logged out, return to your user by exiting `psql`, then typing `exit` to exit the postgres user, and `exit` a SECOND time to exit the root user. 
```
postgres=# \quit
```

```shell
exit
exit 
```

## Rabbitmq Broker Configuration
You have to setup a specific user, and broker host for your augur instance. You can accomplish this by running the below commands:
```shell
sudo rabbitmqctl add_user augur password123 ||
sudo rabbitmqctl add_vhost augur_vhost &&
sudo rabbitmqctl set_user_tags augur augurTag &&
sudo rabbitmqctl set_permissions -p augur_vhost augur ".*" ".*" ".*"
```

NOTE: it is important to have a static hostname when using rabbitmq as it uses hostname to communicate with nodes.

If your setup of rabbitmq is successful your broker url should look like this:

**broker_url = `amqp://augur:password123@localhost:5672/augur_vhost`**

**During Augur installation, you will be prompted for this broker_url**

##  Proxying Augur through Nginx
Assumes nginx is installed. 

Then you create a file for the server you want Augur to run under in the location of your `sites-enabled` directory for nginx (In this example, Augur is running on port 5038: 

```
server {
        listen 80;
        server_name  zoo.chaoss.tv;

        location /api/unstable/ {
                proxy_pass http://zoo.chaoss.tv:5038;
                proxy_set_header Host $host;
        }

	location / {
		proxy_pass http://127.0.0.1:5038;
	}

        error_log /var/log/nginx/augurview.osshealth.error.log;
        access_log /var/log/nginx/augurview.osshealth.access.log;

}
```

## Installing and Configuring Augur!
Create a Python Virtual Environment `python3 -m venv ~/virtual-env-directory` 

Activate your Python Virtual Environment `source ~/virtual-env-directory/bin/activate`

From the root of the Augur Directory, type `make install`

You will be prompted to provide your GitHub username and password, your GitLab username and password, and the postgresql database where you want to have the Augur Schema built. You will also be prompted to provide a directory where repositories will be clone into. 

## Post Installation of Augur

### Redis Broker Configuration
If applications other than Augur are running on the same server, and using `redis-server` it is important to ensure that Augur and these other applications (or additional instances of Augur) are using distinct "cache_group". You can change from the default value of zero by editing the `augur_operations.config` table directly, looking for the "Redis" section_name, and the "cache_group" setting_name. This SQL is also a template: 
```sql
UPDATE augur_operations.config 
SET value = 2
WHERE
section_name='Redis' 
AND 
setting_name='cache_group';
```

## Augur Commands

To access command line options, use `augur --help`. To load repos from GitHub organizations prior to collection, or in other ways, the direct route is `augur db --help`. 

Start a Flower Dashboard, which you can use to monitor progress, and report any failed processes as issues on the Augur GitHub site. The error rate for tasks is currently 0.04%, and most errors involve unhandled platform API timeouts. We continue to identify and add fixes to handle these errors through additional retries. Starting Flower: `(nohup celery -A augur.tasks.init.celery_app.celery_app flower --port=8400 --max-tasks=1000000 &)` NOTE: You can use any open port on your server, and access the dashboard in a browser with http://servername-or-ip:8400 in the example above (assuming you have access to that port, and its open on your network.)

## Starting your Augur Instance
Start Augur: `(nohup augur backend start &)`

When data collection is complete you will see only a single task running in your flower Dashboard.

## Accessing Repo Addition and Visualization Front End
Your Augur intance will now be available at http://hostname.io:port_number

For example: http://chaoss.tv:5038 

Note: Augur will run on port 5000 by default (you probably need to change that in augur_operations.config for OSX)

## Stopping your Augur Instance
You can stop augur with `augur backend stop`, followed by `augur backend kill`. We recommend waiting 5 minutes between commands so Augur can shutdown more gently. There is no issue with data integrity if you issue them seconds apart, its just that stopping is nicer than killing. 

### Docker
1. Make sure docker, and docker-compose are both installed
2. Modify the `environment.txt` file in the root of the repository to include your GitHub and GitLab API keys.
3. If you are already running postgresql on your server you have two choices: 
   - Change the port mappings in the `docker-compose.yml` file to match ports for Postgresql not currently in use.
   - Change to variables in `environment.txt` to include the correct values for your local, non-docker-container database.
4. `sudo docker build -t augur-new -f docker/backend/Dockerfile .`
5. `sudo docker-compose --env-file ./environment.txt --file docker-compose.yml up` to run the database in a Docker Container or 
   `sudo docker-compose --env-file ./environment.txt --file docker-compose.yml up` to connect to an already running database. 

### Errata (Old Frontend)

14. If you have frontend configuration issues that result in a *failure* to complete steps with npm, we recommend you install and use `nvm`: https://tecadmin.net/how-to-install-nvm-on-ubuntu-20-04/ to set your nodejs release to the latest LTS of 12.x or 16.x. For example: `nvm ls-remote | grep -i 'latest'` and `nvm alias default 16.??` (whatever the latest version of 16 is.)
15. Also, please explore our new frontend, being developed at https://github.com/augurlabs/augur_view. The `dev` branch is the most current. 

