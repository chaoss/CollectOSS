---------------------------
Setting up an Augur Server
---------------------------


High-Level Steps to Server Installation of Augur 
------------------------------------------------

1. Have a list of repositories and groups you want them to be in, following the format in the files `schema/repo_group_load_sample.csv` and `schema/repo_load_sample.csv`. 
2. Have access to a server that meets the augur installation pre-requisites (Python, NodeJS, etc).
3. Have nginx installed for front-end service. You can use another HTTP server, but we have instructions for nginx.
4. Make sure you have a database available, owned by a user who has the right to create tables. 
5. Have a GitHub API Key handy.

Detailed Steps
---------------------------

1. Login to your server.
2. Create or activate the Python3 virtual environment for the Augur instance you want to deploy as a public server. 
3. If you have not already done so, clone Augur.
4. Change into that directory.
5. ``git checkout dev``, if you want to deploy the latest features, otherwise remain in the main branch. 
6. You need a database owned by an Augur user. 
7. ``make install`` ... now is a good time to go get some tea.
8. When you return with your tea, follow the prompts: 
        - respond to the SERVER prompt with localhost. 
        - the current standard is to put the repos in a repos/ directory in the root augur directory (these will never get checked in to VC).
9. Load repos, following instructions in docs.
10. If you have more than one instance of Augur or another service on port 5000, you need to edit the ``augur.config.json`` to update the server port:
        - ``sudo lsof -i -P -n | grep LISTEN`` shows you ports in use if you are not sure.
        - ``sudo ufw status`` lets you know if the port you are looking for is available as open through your firewall.
        - ``sudo ufw status | grep 5005`` checks to see if port 5005 is open, for example:
        
                        +---------------+--------+---------------------------------------------+
                        | 5005          | ALLOW  | Anywhere (this line is the most important)  |
                        +---------------+--------+---------------------------------------------+
                        | 5005/tcp      | ALLOW  | Anywhere                                    |
                        +---------------+--------+---------------------------------------------+
                        | 5005/udp      | ALLOW  | Anywhere                                    |
                        +---------------+--------+---------------------------------------------+
                        | 5005 (v6)     | ALLOW  | Anywhere (v6)                               |
                        +---------------+--------+---------------------------------------------+
                        | 5005/tcp (v6) | ALLOW  | Anywhere (v6)                               |
                        +---------------+--------+---------------------------------------------+
                        | 5005/udp (v6) | ALLOW  | Anywhere (v6)                               |
                        +---------------+--------+---------------------------------------------+
                        
11. In the Frontend block of ``augur.config.json``, set the host value to be the domain you want the front end compiled for.  
For example, we set ours to ``test.augurlabs.io``.

.. code-block:: json

    {
    "Frontend": {
            "host": "test.augurlabs.io",
            "port": "5003"
        } 
    }

12. Then do a ``make rebuild-dev``.

Next up: configure ``nginx``!


