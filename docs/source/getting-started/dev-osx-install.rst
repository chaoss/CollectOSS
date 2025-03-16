OSX Setup
===========

**NOTE**: Currently, our machine learning dependencies allow Augur to
only fully support python 3.8 to python 3.10. Python 3.11 will sometimes
work, but often there are libraries at the operating system level that
have not yet been updated to support machine learning libraries at
python 3.11.

For OSX You Need to make sure to install XCode Command line tools:
------------------------------------------------------------------

.. code:: shell

   xcode-select --install

*WARNING: rabbitmq, redis, and postgresql will, by default, set
themselves up to automatically start when your computer starts. This can
be a significant battery drain if you are on battery and not using
Augur. For those reasons, go into your system preferences, startup items
menu (wherever it is now, because Apple changes it more than Zoolander
changes outfits), and turn those “autostart” options off. :)*

*NOTE: If you do not shutoff rabbitmq and redis at the command line
before shutting down, they will restart themselves anyway on restart.
``brew services stop rabbitmq ;brew services stop redis;``*

You also need to install these libraries if you are using apple silicon as of June, 2023
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

brew install gfortran; brew install llvm; echo ‘export
PATH=“/opt/homebrew/opt/llvm/bin:$PATH”’ >> ~/.zshrc; brew install
Pkg-config; brew install openblas;

Add these lines to your .zshrc file:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: shell

   export LDFLAGS="-L/opt/homebrew/opt/llvm/lib"
   export CPPFLAGS="-I/opt/homebrew/opt/llvm/include"
   export LDFLAGS="-L/opt/homebrew/opt/openblas/lib "$LDFLAGS
   export CPPFLAGS="-I/opt/homebrew/opt/openblas/include "$CPPFLAGS
   export PKG_CONFIG_PATH="/opt/homebrew/opt/openblas/lib/pkgconfig"

Git Platform Requirements (Things to have setup prior to initiating installation.)
----------------------------------------------------------------------------------

1. Obtain a GitHub Access Token: https://github.com/settings/tokens
2. Obtain a GitLab Access Token: https://gitlab.com/-/user_settings/personal_access_tokens

Fork and Clone Augur
~~~~~~~~~~~~~~~~~~~~

1. Fork https://github.com/chaoss/augur
2. Clone your fork. We recommend creating a ``github`` directory in your
   user’s base directory.

Pre-Requisite Operating System Level Packages
---------------------------------------------

Here we ensure your system is up to date, install required python
libraries, install postgresql, and install our queuing infrastrucutre,
which is composed of redis-server and rabbitmq-server

Updating your Path: Necessary for rabbitmq on OSX
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

for macOS Intel
^^^^^^^^^^^^^^^

``export PATH=$PATH:/usr/local/sbin`` #### for Apple Silicon
``export PATH=$PATH:/opt/homebrew/sbin``

**These should be added to your .zshrc or other environment file loaded
when you open a terminal**

.. _for-macos-intel-1:

for macOS Intel
^^^^^^^^^^^^^^^

``export PATH=$PATH:/usr/local/sbin:$PATH`` #### for Apple Silicon
``export PATH=$PATH:/opt/homebrew/sbin:$PATH``

Executable
~~~~~~~~~~

.. code:: shell

   brew update ; 
   brew upgrade ; 
   brew install rabbitmq ; 
   brew install redis ;
   brew install postgresql@14 ;
   brew install python3-yq ; 
   brew install python@3.11 ;
   brew install postgresql@14 ; 
   brew install go ; #required: Go Needs to be version 1.19.x or higher.
   brew install nginx ; # required for hosting
   brew install geckodriver; 

   # You will almost certainly need to reboot after this. 

RabbitMQ Configuration
~~~~~~~~~~~~~~~~~~~~~~

The default timeout for RabbitMQ needs to be set.

.. code:: shell

   sudo vi /opt/homebrew/etc/rabbitmq/advanced.config

Add this one line to that file (the period at the end matters):

.. code:: shell

   [ {rabbit, [ {consumer_timeout, undefined} ]} ].

Rabbitmq Broker Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You have to setup a specific user, and broker host for your augur
instance. You can accomplish this by running the below commands:

.. code:: shell

   rabbitmq-plugins enable rabbitmq_management;
   rabbitmqctl add_user augur password123;
   rabbitmqctl add_vhost augur_vhost;
   rabbitmqctl set_user_tags augur augurTag administrator;
   rabbitmqctl set_permissions -p augur_vhost augur ".*" ".*" ".*";

-  We need rabbitmq_management so we can purge our own queues with an
   API call
-  We need a user
-  We need a vhost
-  We then set permissions

NOTE: it is important to have a static hostname when using rabbitmq as
it uses hostname to communicate with nodes.

If your setup of rabbitmq is successful your broker url should look like
this:

**broker_url = ``amqp://augur:password123@localhost:5672/augur_vhost``**

You will be asked for the broker URL on install of Augur. You can copy
and paste the line above
(``amqp://augur:password123@localhost:5672/augur_vhost``) if you created
the users and virtual hosts under “Broker Configuration”, above.

Things to start before augur later
----------------------------------

.. code:: shell

   brew services start rabbitmq ;
   brew services start redis;
   brew services start postgresql@14;

If Issues Starting rabbitmq
~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you get this error:

::

   brew services start rabbitmq
   Bootstrap failed: 5: Input/output error
   Try re-running the command as root for richer errors.
   Error: Failure while executing; `/bin/launchctl bootstrap gui/501 /Users/sean/Library/LaunchAgents/homebrew.mxcl.rabbitmq.plist` exited with 5.

Execute this command:

::

   launchctl unload -w /Users/sean/Library/LaunchAgents/homebrew.mxcl.rabbitmq.plist

Replace the specific path with the one after
``/Users/sean/Library/LaunchAgents/`` in your error message. This was
tested on Apple Silicon.

Git Configuration
-----------------

There are some Git configuration parameters that help when you are
cloning repos over time, and a platform prompts you for credentials when
it finds a repo is deleted:

.. code:: shell

       git config --global diff.renames true;
       git config --global diff.renameLimit 200000;
       git config --global credential.helper cache;
       git config --global credential.helper 'cache --timeout=9999999999999';

Postgresql Configuration
------------------------

Create a PostgreSQL database for Augur to use

.. code:: shell

   ... really varies depending how you installed postgres. TBD

Then, from within the resulting postgresql shell:

.. code:: sql

   CREATE DATABASE augur;
   CREATE USER augur WITH ENCRYPTED PASSWORD 'password';
   GRANT ALL PRIVILEGES ON DATABASE augur TO augur;
   GRANT ALL ON SCHEMA public TO augur;

After that, return to your user by exiting ``psql``

::

   postgres=# \quit

Here we want to start an SSL connection to the ``augur`` database on
port 5432:

.. code:: shell

   psql -h localhost -U postgres -p 5432

Now type ``exit`` to log off the postgres user, and ``exit`` a SECOND
time to log off the root user.

.. code:: shell

   exit
   exit 

RabbitMQ Developer Note:
~~~~~~~~~~~~~~~~~~~~~~~~

These are the queues we create: - celery (the main queue) - secondary -
scheduling

The endpoints to hit to purge queues on exit are:

::

   curl -i -u augur:password123 -XDELETE http://localhost:15672/api/queues/augur_vhost/celery

   curl -i -u augur:password123 -XDELETE http://localhost:15672/api/queues/augur_vhost/secondary

   curl -i -u augur:password123 -XDELETE http://localhost:15672/api/queues/augur_vhost/scheduling

We provide this functionality to limit, as far as possible, the need for
sudo privileges on the Augur operating system user. With sudo, you can
accomplish the same thing with (Given a vhost named AugurB [case
sensitive]):

1. To list the queues

::

   rabbitmqctl list_queues -p AugurB name messages consumers

2. To empty the queues, simply execute the command for your queues.
   Below are the 3 queues that Augur creates for you:

::

   rabbitmqctl purge_queue celery -p augur_vhost
   rabbitmqctl purge_queue secondary -p augur_vhost
   rabbitmqctl purge_queue scheduling -p augur_vhost

Where augur_vhost is the vhost. The management API at port 15672 will
only exist if you have already installed the rabbitmq_management plugin.

**During Augur installation, you will be prompted for this broker_url**

Installing and Configuring Augur!
---------------------------------

Create a Python Virtual Environment
``python3 -m venv ~/virtual-env-directory``

Activate your Python Virtual Environment
``source ~/virtual-env-directory/bin/activate``

From the root of the Augur Directory, type ``make install``. You will be
prompted to provide:

-  “User” is the PSQL database user, which is ``augur`` if you followed
   instructions exactly
-  “Password” is the above user’s password
-  “Host” is the domain used with nginx, e.g. ``ai.chaoss.io``
-  “Port” is 5432 unless you reconfigured something
-  “Database” is the name of the Augur database, which is ``augur`` if
   you followed instructions exactly
-  The GitHub token created earlier
-  Then the username associated with it
-  Then the same for GitLab
-  and finally a directory to clone repositories to

Post Installation of Augur
--------------------------

Redis Broker Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~

If applications other than Augur are running on the same server, and
using ``redis-server`` it is important to ensure that Augur and these
other applications (or additional instances of Augur) are using distinct
“cache_group”. You can change from the default value of zero by editing
the ``augur_operations.config`` table directly, looking for the “Redis”
section_name, and the “cache_group” setting_name. This SQL is also a
template:

.. code:: sql

   UPDATE augur_operations.config 
   SET value = 2
   WHERE
   section_name='Redis' 
   AND 
   setting_name='cache_group';

What does Redis Do?
^^^^^^^^^^^^^^^^^^^

Redis is used to make the state of data collection jobs visible on an
external dashboard, like Flower. Internally, Augur relies on Redis to
cache GitHub API Keys, and for OAuth Authentication. Redis is used to
maintain awareness of Augur’s internal state.

What does RabbitMQ Do?
^^^^^^^^^^^^^^^^^^^^^^

Augur is a distributed system. Even on one server, there are many
collection processes happening simultaneously. Each job to collect data
is put on the RabbitMQ Queue by Augur’s “Main Brain”. Then independent
workers pop messages off the RabbitMQ Queue and go collect the data.
These tasks then become standalone processes that report their
completion or failure states back to the Redis server.

**Edit** the ``/etc/redis/redis.conf`` file to ensure these parameters
are configured in this way:

.. code:: shell

   supervised systemd
   databases 900
   maxmemory-samples 10
   maxmemory 20GB

**NOTE**: You may be able to have fewer databases and lower maxmemory
settings. This is a function of how many repositories you are collecting
data for at a given time. The more repositories you are managing data
for, the close to these settings you will need to be.

**Consequences** : If the settings are too low for Redis, Augur’s
maintainer team has observed cases where collection appears to stall.
(TEAM: This is a working theory as of 3/10/2023 for Ubuntu 22.x, based
on EC2 experiments.)

(OPTIONAL: NOT FOR DEV: Proxying Augur through Nginx)
-----------------------------------------------------

Assumes nginx is installed.

Then you create a file for the server you want Augur to run under in the
location of your ``sites-enabled`` directory for nginx. In this example,
Augur is running on port 5038: (the long timeouts on the settings page
is for when a user adds a large number of repos or orgs in a single
session to prevent timeouts from nginx)

.. _for-macos-intel-2:

For MacOS Intel:
~~~~~~~~~~~~~~~~

This gist explains where sites-enabled is:
``https://gist.github.com/jimothyGator/5436538``

Logs for nginx should go in this directory:

``mkdir /Library/Logs/nginx``

``/Library/Logs/nginx``

For Apple Silicon:
~~~~~~~~~~~~~~~~~~

There is no ``sites-enabled`` directory. Server configurations go here:
``/opt/homebrew/etc/nginx/servers``

Logs for nginx should go in this directory:
``/opt/homebrew/var/log/nginx``

::

   server {
           server_name  ai.chaoss.io;

           location /api/unstable/ {
                   proxy_pass http://ai.chaoss.io:5038;
                   proxy_set_header Host $host;
           }

           location / {
                   proxy_pass http://127.0.0.1:5038;
           }

           location /settings {

                   proxy_read_timeout 800;
                   proxy_connect_timeout 800;
                   proxy_send_timeout 800;
           }

           error_log /var/log/nginx/augurview.osshealth.error.log;
           access_log /var/log/nginx/augurview.osshealth.access.log;

   }

(OPTIONAL: NOT FOR DEV) Setting up SSL (https)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install Certbot: **NOTE: certbot does not currently run on Apple
Silicon, as it is looking for information in MacOS Intel directories**

::

   brew update;
   brew upgrade;
   brew install certbot;
   brew install openssl; 
   brew install brew install python-typing-extensions

Generate a certificate for the specific domain for which you have a file
already in the sites-enabled directory for nginx (located at
``/etc/nginx/sites-enabled`` on Ubuntu):

::

    brew certbot -v --nginx  -d ai.chaoss.io

In the example file above. Your resulting nginx sites-enabled file will
look like this:

::

   server {
           server_name  ai.chaoss.io;

           location /api/unstable/ {
                   proxy_pass http://ai.chaoss.io:5038;
                   proxy_set_header Host $host;
           }

      location / {
         proxy_pass http://127.0.0.1:5038;
      }

      location /settings {

                   proxy_read_timeout 800;
                   proxy_connect_timeout 800;
                   proxy_send_timeout 800;
      }

           error_log /var/log/nginx/augurview.osshealth.error.log;
           access_log /var/log/nginx/augurview.osshealth.access.log;

       listen 443 ssl; # managed by Certbot
       ssl_certificate /etc/letsencrypt/live/ai.chaoss.io/fullchain.pem; # managed by Certbot
       ssl_certificate_key /etc/letsencrypt/live/ai.chaoss.io/privkey.pem; # managed by Certbot
       include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
       ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot

   }

   server {
       if ($host = ai.chaoss.io) {
           return 301 https://$host$request_uri;
       } # managed by Certbot


           listen 80;
           server_name  ai.chaoss.io;
       return 404; # managed by Certbot


   }

Possible EC2 Configuration Requirements
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

With virtualization there may be issues associated with redis-server
connections exceeding available memory. In these cases, the following
workarounds help to resolve issues.

Specifically, you may find this error in your augur logs:

.. code:: shell

   redis.exceptions.ConnectionError: Error 111 connecting to 127.0.0.1:6379. Connection refused.

**INSTALL** ``sudo apt install libhugetlbfs-bin``

**COMMAND**:

::

   sudo hugeadm --thp-never &&
   sudo echo never > /sys/kernel/mm/transparent_hugepage/enabled

.. code:: shell

   sudo vi /etc/rc.local

**paste** into ``/etc/rc.local``

.. code:: shell

   if test -f /sys/kernel/mm/transparent_hugepage/enabled; then
      echo never > /sys/kernel/mm/transparent_hugepage/enabled
   fi

**EDIT** : ``/etc/default/grub`` add the following line:

.. code:: shell

   GRUB_DISABLE_OS_PROBER=true

.. _postgresql-configuration-1:

Postgresql Configuration
------------------------

Your postgresql instance should optimally allow 1,000 connections:

.. code:: shell

   max_connections = 1000                  # (change requires restart)
   shared_buffers = 8GB                    # min 128kB
   work_mem = 2GB                  # min 64kB

Augur will generally hold up to 150 simultaneous connections while
collecting data. The 1,000 number is recommended to accommodate both
collection and analysis on the same database. Use of PGBouncer or other
utility may change these characteristics.

Augur Commands
--------------

To access command line options, use ``augur --help``. To load repos from
GitHub organizations prior to collection, or in other ways, the direct
route is ``augur db --help``.

Start a Flower Dashboard, which you can use to monitor progress, and
report any failed processes as issues on the Augur GitHub site. The
error rate for tasks is currently 0.04%, and most errors involve
unhandled platform API timeouts. We continue to identify and add fixes
to handle these errors through additional retries. Starting Flower:
``(nohup celery -A augur.tasks.init.celery_app.celery_app flower --port=8400 --max-tasks=1000000 &)``
NOTE: You can use any open port on your server, and access the dashboard
in a browser with http://servername-or-ip:8400 in the example above
(assuming you have access to that port, and its open on your network.)

If you’re using a virtual machine within Windows and you get an error
about missing AVX instructions, you should kill Hyper-V. Even if it
doesn’t *appear* to be active, it might still be affecting your VM.
Follow `these instructions <https://stackoverflow.com/a/68214280>`__ to
disable Hyper-V, and afterward AVX should pass to the VM.

Starting your Augur Instance
----------------------------

Start Augur: ``(nohup augur backend start &)``

When data collection is complete you will see only a single task running
in your flower Dashboard.

Accessing Repo Addition and Visualization Front End
---------------------------------------------------

Your Augur instance will now be available at
http://hostname.io:port_number

For example: http://chaoss.tv:5038

Note: Augur will run on port 5000 by default (you probably need to
change that in augur_operations.config for OSX)

Stopping your Augur Instance
----------------------------

You can stop augur with ``augur backend stop``, followed by
``augur backend kill``. We recommend waiting 5 minutes between commands
so Augur can shutdown more gently. There is no issue with data integrity
if you issue them seconds apart, its just that stopping is nicer than
killing.

Docker
~~~~~~

1. Make sure docker, and docker compose are both installed
2. Modify the ``environment.txt`` file in the root of the repository to
   include your GitHub and GitLab API keys.
3. If you are already running postgresql on your server you have two
   choices:

   -  Change the port mappings in the ``docker-compose.yml`` file to
      match ports for Postgresql not currently in use.
   -  Change to variables in ``environment.txt`` to include the correct
      values for your local, non-docker-container database.

4. ``sudo docker build -t augur-new -f docker/backend/Dockerfile .``
5. ``sudo docker compose --env-file ./environment.txt --file docker-compose.yml up``
   to run the database in a Docker Container or
   ``sudo docker compose --env-file ./environment.txt --file docker-compose.yml up``
   to connect to an already running database.
