Setting up an Augur Server
---------------------------

High Level Steps to Server Installation of Augur 

List of repositories and groups you want them to be in
Access to a computer that meets the augur installation pre-requistites
Nginx for front end service 

Detailed Steps

Login to Mudcats.augurlabs.io 
Create virtual environment … standard on mudcats ..
I’ve taken to keeping all the virtualenvs here: /home/sean/github/virtualenvs
Each virtualenv gets a -color appendix so I can have multiple for each instance in case I need that. It also facilitates checking what is changed on rebuild. 
python3 -m venv /home/sean/github/virtualenvs/<env_name>
Clone Augur into a new directory under github.  SO, if you created an environment like augur-test-blue, you would do a git clone https://github.com/chaoss/augur augur-test from the /home/sean/github directory. 
Change into that directory
Git checkout dev
You’ll need a database owned by augur. 
Do a make install from the command line, and follow the prompts. And now is the time to go get some tea. 
If both the database and augur are on mudcats, make sure the host is localhost
Current standard is to put the repos in a repos/ directory in the root augur directory (these will never get checked in to VC)
Load repos, following instructions in docs. 
Set the augur port on the server: sudo lsof -i -P -n | grep LISTEN  … this will show you ports in use. 
Check to see if the firewall is open for a port: sudo ufw status
Output should resemble this:
5005                       ALLOW       Anywhere *** this line is the most important
5005/tcp                   ALLOW       Anywhere
5005/udp                   ALLOW       Anywhere
5005 (v6)                  ALLOW       Anywhere (v6)
5005/tcp (v6)              ALLOW       Anywhere (v6)
5005/udp (v6)              ALLOW       Anywhere (v6)
Set the server to be the domain you want the front end compiled for.  For example, we set ours to test.augurlabs.io 
Then do a make rebuild
Configure nginx: You need a file named whatever your domain is inside of the /etc/nginx/sites-enabled directory.  Ours is test.augurlabs.io

server {
        server_name  test.augurlabs.io;

        root /home/sean/github/augur-test/frontend/dist;
        index index.html index.htm;

        location / {
        root /home/sean/github/augur-test/frontend/dist;
        try_files $uri $uri/ /index.html;
        }


        location /api_docs/ {
        root /home/sean/github/augur-test/frontend/public;
        index index.html;
        }


        error_log /var/log/nginx/augur.test.augurlabs.io.error.log;
        access_log /var/log/nginx/augur.test.augurlabs.io.access.log;



}
sudo nginx -t to make sure its configured correctly. nginx: 
the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
sudo systemctl restart nginx 
Comment out the contributors model in the housekeeper block of augur.config.json 
To start augur on the server: 
nohup augur run >augur.log 2>augur.err &
cd workers 
cd facade_worker
nohup facade_worker_start >f.log 2>f.err &
cd ../github_worker 


