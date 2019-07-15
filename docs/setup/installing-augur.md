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
2. Create a user called "augur" and a database called "augur" in your postgresql database system. Then grant the user all the rights on the database. 

### Command Line Strategy

```
    sudo -u postgres psql
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

3. Execute the file named [`new-augur.0.0.77.5-release.sql`](../../augur/persistence_schema/new-augur.0.0.77.5-release.sql) as the `augur` user, if you have granted that user schema creation privileges, or as any other user who has schema creation privileges.  All schemas, the tables, and sequences they contain, are owned by the `augur` user. Sure, you could do a search and replace and make everything owned by `Sarah`, but why would you do that? Unless your name is `Sarah` and its really important to you. 
4. There is also a small amount of "seed data" that our data collection "workers" need populated, so execute the file named [`seed_data.sql`](../../augur/persistence_schema/new-augur.0.0.77.5-release.sql) as the `augur` user as well. 

## Build Your Augur Backend Environment
1. `pip install pipreqs sphinx`
2. `sudo npm install -g apidoc brunch newman` 
3. `pip install -e .` 
4. `pip install ipykernel`
5. `pip install xlsxwriter` (you will need this for the facade worker later)
5. `python -m ipykernel install --user --name augur --display-name "Python (augur)"`

## Augur Back End
1. Create a file in the root of your augur project called `augur.config.json`. [Here is a sample augur.config.json file](./augur-sample-cnfg.json). There are a number of places where you need to provide
    - Augur database credentials
    - Login to GitHub.com, then create [A GitHub API Key](https://github.com/settings/tokens)  
    - API Keys for optional services
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

