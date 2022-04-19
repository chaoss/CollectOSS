# SSL Configuration Notes:



COPY the certbot .pem keys generated into this directory. 

Then `chmod youruser *` and 

`chgrp yourgroup *`


--------------------
Enabling HTTPS
--------------------

HTTPS is an extension of HTTP. It is used for secure communications over a computer networks by encrypting your data so it is not vulnerable to MIM(Man-in-the-Middle) attacks etc. While Augur's API data might not be very sensitive, it would still be a nice feature to have so something can't interfere and provide wrong data. Additionally, the user may not feel very comfortable using an application when the browser is telling the user it is not secure. Features such as logins is an example of information that would be particularly vulnerable to attacks. Lastly, search engine optimization actually favors applications on HTTPS over HTTP.

This guide will start on a fully configured EC2 Ubuntu 20.04 instance, meaning it is assumed to already have Augur installed and running with all of its dependencies(PostgreSQL, Nginx, etc).

~~~~~~~~~~~~~~~~~~~~~
Let's Encrypt/Certbot
~~~~~~~~~~~~~~~~~~~~~

The easiest way to get an HTTPS server up is to make use of `Let's Encrypt <https://letsencrypt.org/>`_'s `Certbot <https://certbot.eff.org/>`_ tool. It is an open source tool that is so good it will even alter the nginx configuration for you automatically to enable HTTPS. Following their guide for ``Ubuntu 20.04``, run ``sudo snap install --classic certbot``, ``sudo ln -s /snap/bin/certbot /usr/bin/certbot``, and then ``sudo certbot --nginx``.

~~~~~~~~~~~~~~~~~~~~
Fixing the Backend
~~~~~~~~~~~~~~~~~~~~

Now our server is configured properly and our frontend is being served over HTTPS, but there's an extra problem: the backend APIs are still being served over HTTP resulting in a ``blocked loading mixed active content`` error. This issue is currently being looked into by our developers. Some files that are candidates for causing issues here are ``augur/application.py``, ``frontend/src/AugurAPI.ts``, and ``frontend/src/router.ts``.
