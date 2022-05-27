Web Server Configuration
-------------------------------------

Configuring nginx for Augur to run behind nginx requires you to have certain options available for symlinks and other basic nginx options. The `nginx.conf` file below is one example of a configuration known to work.

Once you have nginx configured, run these commands to make sure everything is loaded and configured correctly:

1. ``sudo nginx -t`` to make sure it's configured correctly.
	`nginx: the configuration file /etc/nginx/nginx.conf syntax is ok`
	`nginx: configuration file /etc/nginx/nginx.conf test is successful`
2. ``sudo systemctl restart nginx`` on Ubuntu.
3. sudo nginx on OS X.

--------------------------
Server Compilation
--------------------------

**Your Augur instance must compile with a publicly accessible domain that the frontend instance will be able to access.**

1. Your ``augur.config.json`` server block **must** be set like this:

.. code-block:: json

	{
	    "Server": {
	        "cache_expire": 3600,
	        "host": "subdomain.domain.tld",
	        "port": "5000",
	        "workers": 8
	    }
    }

2.   Compile Augur (this wires the host and port into the frontend so people pulling the web pages of Augur, in the `frontend/` subdirectory are referring to the right endpoints for this instance.): ``make rebuild``
3.   Run Augur: ``nohup augur backend start >augur.log 2>augur.err &``


------------------
nginx
------------------

------------------
nginx.conf
------------------

.. code-block::

	user www-data;
	worker_processes auto;
	pid /run/nginx.pid;
	include /etc/nginx/modules-enabled/*.conf;

	worker_rlimit_nofile 30000;

	events {
		worker_connections 768;
		# multi_accept on;
	}

	http {

		##
		# Basic Settings
		##
		disable_symlinks off;

		sendfile on;
		tcp_nopush on;
		tcp_nodelay on;
		keepalive_timeout 65;
		types_hash_max_size 2048;
		# server_tokens off;

		 server_names_hash_bucket_size 64;
		# server_name_in_redirect off;

		include /etc/nginx/mime.types;
		default_type application/octet-stream;

		##
		# SSL Settings
		##

		ssl_protocols TLSv1 TLSv1.1 TLSv1.2 TLSv1.3; # Dropping SSLv3, ref: POODLE
		ssl_prefer_server_ciphers on;

		##
		# Logging Settings
		##

		access_log /var/log/nginx/access.log;
		error_log /var/log/nginx/error.log;

		##
		# Gzip Settings
		##

		gzip on;

		# gzip_vary on;
		# gzip_proxied any;
		# gzip_comp_level 6;
		# gzip_buffers 16 8k;
		# gzip_http_version 1.1;
		# gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

		##
		# Virtual Host Configs
		##

		include /etc/nginx/conf.d/*.conf;
		include /etc/nginx/sites-enabled/*;
	}

--------------------
Site Configuration
--------------------

This file will be located in the ``/etc/nginx/sites-enabled`` directory on most Linux distributions.  Mac OSX keeps these files in the ``/usr/local/etc/nginx/sites-enabled`` directory. **Note that Augur's backend server must be running**

.. code-block::

		server {
		        listen 80;
		        server_name  <<your server subdomain.domain.tld>>;

		        root /home/user/.../<<augur-instance-home>>/frontend/dist;
		        index index.html index.htm;

		        location / {
		        root /home/user/.../<<augur-instance-home>>/frontend/dist;
		        try_files $uri $uri/ /index.html;
		        }

		#        location /api/unstable/ {
		#                proxy_pass http://census.osshealth.io:5000;
		#                proxy_set_header Host $host;
		#        }

		        location /api_docs/ {
		        root /home/user/.../<<augur-instance-home>>/frontend/dist;
		        index index.html;
		        }


		        error_log /var/log/nginx/augur.censusscienceosshealth.error.log;
		        access_log /var/log/nginx/augur.censusscienceosshealth.access.log;

		}
    
--------------------
Enabling HTTPS
--------------------

HTTPS is an extension of HTTP. It is used for secure communications over a computer networks by encrypting your data so it is not vulnerable to MIM(Man-in-the-Middle) attacks etc. While Augur's API data might not be very sensitive, it would still be a nice feature to have so something can't interfere and provide wrong data. Additionally, the user may not feel very comfortable using an application when the browser is telling the user it is not secure. Features such as logins is an example of information that would be particularly vulnerable to attacks. Lastly, search engine optimization actually favors applications on HTTPS over HTTP.

This guide will start on a fully configured EC2 Ubuntu 20.04 instance, meaning it is assumed to already have Augur installed and running with all of its dependencies(PostgreSQL, Nginx, etc).

~~~~~~~~~~~~~~~~~~~~
Let's Encrypt/Certbot
~~~~~~~~~~~~~~~~~~~~

The easiest way to get an HTTPS server up is to make use of `Let's Encrypt <https://letsencrypt.org/>`_'s `Certbot <https://certbot.eff.org/>`_ tool. It is an open source tool that is so good and it will even alter the nginx configuration for you automatically to enable HTTPS. Following their guide for ``Ubuntu 20.04``, run ``sudo snap install --classic certbot``, ``sudo ln -s /snap/bin/certbot /usr/bin/certbot``, and then ``sudo certbot --nginx``.

.. code-block:: bash

	# Example Certificate Response Using Certbot

	Which names would you like to activate HTTPS for?
	- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	1: augur.augurlabs.io
	2: new.augurlabs.io
	3: old.augurlabs.io
	4: augur.chaoss.io
	- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	Select the appropriate numbers separated by commas and/or spaces, or leave input
	blank to select all options shown (Enter 'c' to cancel): 4
	Requesting a certificate for augur.chaoss.io

	Successfully received certificate.
	Certificate is saved at: /etc/letsencrypt/live/augur.chaoss.io/fullchain.pem
	Key is saved at:         /etc/letsencrypt/live/augur.chaoss.io/privkey.pem
	This certificate expires on 2022-07-12.
	These files will be updated when the certificate renews.
	Certbot has set up a scheduled task to automatically renew this certificate in the background.

	Deploying certificate
	Successfully deployed certificate for augur.chaoss.io to /etc/nginx/sites-enabled/augur.chaoss.io
	Congratulations! You have successfully enabled HTTPS on https://augur.chaoss.io

	- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	If you like Certbot, please consider supporting our work by:
	 * Donating to ISRG / Let's Encrypt:   https://letsencrypt.org/donate
	 * Donating to EFF:                    https://eff.org/donate-le


~~~~~~~~~~~~~~~~~~~
Fixing the Backend
~~~~~~~~~~~~~~~~~~~

Now our server is configured properly and our frontend is being served over HTTPS, but there's an extra problem: the backend APIs are still being served over HTTP resulting in a ``blocked loading mixed active content`` error. This issue is a deep rooted issue and several files need to be modified to accomodate HTTPS.

First, we will start with lines 29, 33, & 207 of ``augur/frontend/src/AugurAPI.ts`` and rewrite the URL to use the HTTPS protocol instead of HTTP. We will then do this again in ``augur/frontend/src/common/index.tx`` & ``augur/frontend/src/compare/index.ts`` where the ``AugurAPI`` constructor was called and passed an HTTP protocol. Next we need to configure gunicorn in the backend to support our SSL certificates, but by default certbot places these in a directory that requires root access. Copy these files by running ``sudo cp /etc/letsencrypt/live/<server name here>/fullchain.pem /home/ubuntu/augur/fullchain.pem`` and ``sudo cp /etc/letsencrypt/live/<server name here>/privkey.pem /home/ubuntu/augur/privkey.pem`` into augur's root directory, then change the user and group permissions with ``sudo chown ubuntu <filename.pem>`` and ``sudo chgrp ubuntu <filename.pem`` for both pem files. Now that the user permissions are set properly, gunicorn should be able to access them but we still need to add them to our gunicorn configuration document in ``augur/application.py``. Change the corresponding code block to look like this:

.. code-block:: python

    self.gunicorn_options = {
            'bind': '%s:%s' % (self.config.get_value("Server", "host"), self.config.get_value("Server", "port")),
            'workers': int(self.config.get_value('Server', 'workers')),
            'timeout': int(self.config.get_value('Server', 'timeout')),
            'certfile': '/home/ubuntu/augur/fullchain.pem',
            'keyfile': '/home/ubuntu/augur/privkey.pem'
        }


