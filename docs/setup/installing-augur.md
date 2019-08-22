# Augur Install Steps

## Setup a Python Environment
### Ubuntu 
1. Update Python to 3.7: 
    - `sudo apt-get install python3.7`
    - `sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.7 2`
    - `sudo update-alternatives --config python3` 
        - Select the option for Python 3.7
2. Install Python's Virtual Environment Tool: `pip3 install virtualenv`
3. Change to your "home directory" for the next step. For all the operating systems we are aware of, you accomplish this simply by typing `cd` and then pressing enter at the command line. 
4. Create a Python 3 virtual environment for Augur: `virtualenv --python=python3 newaugur`
5. Activate your virtual environment `source newaugur/bin/activate` (In the case of Ubuntu, you get the `source` command automatically put into your path using the `bash` shell. So, if you get an error, type `bash` and then hit the enter key and try again.)
6. Make sure you have NodeJS and NPM installed. `sudo dnf install nodejs` on Fedora or `sudo apt-get install nodejs` on Ubuntu. Or `brew install nodejs` on a Mac. 

### Other operating systems
1. For Mac OSX `sudo apt-get install` is replaced with `brew install`. [To download brew, click here.](https://brew.sh/) 
2. For Fedora based Linux distributions, `sudo apt-get install` is replaced with `sudo dnf install`
3. Python instructions are the same on all operating systems except for windows. We currently have a Vagrant distribution on Windows, and will update that distribution with the latest version of Augur by August 1, 2019. 

## Getting Augur
1. Clone the Augur Repository: `git clone https://github.com/chaoss/augur.git`
2. Change into the `augur` directory with `cd augur`
3. Switch to the dev branch:  `git checkout dev`

## Create Database Schema
1. [Install Postgresql's latest version for your operating system.](https://www.postgresql.org/download/)
    - You should download and install the database engine for your operating system. For Mac, you can use `brew install postgresql` as an efficient shortcut. 
    - Then you will have either a command line or web interface strategy (described below) to follow for administration and script running. 
2. Create a user called "augur" and a database called "augur" in your postgresql database system. Then grant the user all the rights on the database. 

### Command Line Strategy
**For Linux**
```
    sudo -u postgres psql
    postgres=# create database augur;
    postgres=# create user augur with encrypted password 'mypass';
    postgres=# grant all privileges on database augur to augur;

```

**For Mac OSX**  
```
    $ pgsql postgres
    postgres=# create database augur;
    postgres=# create user augur with encrypted password 'mypass';
    postgres=# grant all privileges on database augur to augur;
```


### GUI Strategy 
- Download pgadmin: https://www.pgadmin.org/download/
- Configure pgadmin for your local or remote database environment
- You can get more information from these links: 
    - Support: pgadmin-support@lists.postgresql.org
    - Website: https://www.pgadmin.org/
    - Tracker: https://redmine.postgresql.org/projects/pgadmin4
- Create your database `augur`
- Create your user `augur` with a password. 
- Grant augur all the privileges on augur

## Create the database schema

3. Download a startup copy of the database with some sample data: [nekocase.augurlabs.io/augur.psql.bak.gz](nekocase.augurlabs.io/augur.psql.bak.gz)
4. `gunzip augur.psql.bak.gz`
4. `psql augur < augur.psql.bak` ; provide the password when prompted
4. Configure
    - Edit the `pg_hba.conf` file to have all local connections use MD5 authentication. Go to the very bottom of the file, and make sure it looks like this. On most Linux distros it is located in `/etc/postgresql/11/main/pg_hba.conf`
```
            # Database administrative login by Unix domain socket
            local   all             postgres                                peer

            # TYPE  DATABASE        USER            ADDRESS                 METHOD

            # "local" is for Unix domain socket connections only
            local   all             all                                     md5 
            # IPv4 local connections:
            host    all             all             0.0.0.0/0               md5
            # IPv6 local connections:
            host    all             all             ::1/128                 md5
            # Allow replication connections from localhost, by a user with the
            # replication privilege.
            local   replication     all                                     peer
            host    replication     all             127.0.0.1/32            md5
            host    replication     all             ::1/128                 md5
```

## Build Your Augur Backend Environment
From the root directory inside of your augur clone (assuming an activated Python virtualenv from the beginning steps: `source newaugur/bin/activate`)
1. `pip install pipreqs sphinx`
2. `npm install -g apidoc brunch newman` 
3. If you are building for a second time, `rm -rf build/*`
3. `pip install -e .` 
4. `pip install ipykernel`
5. `pip install xlsxwriter` (you will need this for the facade worker later)
5. `python -m ipykernel install --user --name augur --display-name "Python (augur)"`
6. `python setup.py install`

## Augur Back End
1. Create a file in the root of your augur project called `augur.config.json`. [Here is a sample augur.config.json file](./augur-sample-cnfg.json). There are a number of places where you need to provide
    - Augur database credentials
        ```
            "Database": {
                "connection_string": "sqlite:///:memory:",
                "database": "augur",
                "name": "your database name here",
                "host": "your hostname, probably localhost for development",
                "password": "your password",
                "port": "your postgres port, probably 5432",
                "schema": "augur_data",
                "user": "augur",
                "key": "your github API key",
                "zombie_id": "22"
            },
        ```
    - Request credentials for GHTorrent Public Instance
```
            "GHTorrent": {
                "host": " request public GHTorrent Access by commenting here: https://github.com/chaoss/augur/issues/302",
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
```
    - Login to GitHub.com, then create [A GitHub API Key](https://github.com/settings/tokens)  
```
            "GitHub": {
                "apikey": "Your GitHub API Key"
            },
```
2. Once this is complete, you can start Augur `augur run`
3. If there are no error messages continuously streaming, you can stop the process with 'ctrl+c', or leave it running and open a new terminal window for the backend. If you want to run it in the background: 
    - To start: `nohup augur run >> augur.log 2 >> augur.err &`
    - To stop: `ps aux | grep -ie augur | awk '{print "kill -9 " $2}'` will create a series of "kill" commands. Copy them and paste them into your terminal. 

## Augur Front End
### Start Front End for Development
1. From the root of the augur .git repository: `cd frontend`
2. `npm install`
3. To start a development Server: `npm run serve`. This will let you see the emerging front end on local host. (Note, as of right now its "empty", however you can see an example of our old front end running on http://dev.augurlabs.io/)  

### Start Front End for Deployment on a Server
1. The Dev branch is actively being developed, and these instructions are evolving 
2. [This is the most current version of our server deployment instruction for the front end](./augur-deployment.md)

