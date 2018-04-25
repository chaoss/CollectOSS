# Augur

branch | status
   --- | ---
master | [![Build Status](https://travis-ci.org/OSSHealth/augur.svg?branch=master)](https://travis-ci.org/OSSHealth/augur)
   dev | [![Build Status](https://travis-ci.org/OSSHealth/augur.svg?branch=dev)](https://travis-ci.org/OSSHealth/augur)

Augur is a Python library and REST server that provides data related to GitHub repositories. Hosting the Augur project requires a copy of the [GHTorrent database](http://ghtorrent.org/downloads.html).

Augur is under heavy development; expect frequent backwards-incompatible changes until a 1.x.x release!



Roadmap
-------
Our technical, outreach, and academic goals [roadmap](https://github.com/OSSHealth/augur/wiki/Release-Schedule).



Installation with Docker (easy to get up and running)
-----------------------------------------------------
Before we begin, make sure you have everything you need installed: [Git](https://git-scm.com/downloads), [Docker](https://www.docker.com/community-edition), [Docker Compose](https://docs.docker.com/compose/install/), and a MySQL server with [GHTorrent](https://github.com/gousiosg/github-mirror/tree/master/sql) loaded.

Now, to install:

1.  Clone the repo and enter its directory:

    ```bash
    git clone https://github.com/OSSHealth/augur
    cd augur
      ```


2.  Set the following variables in your environment:

    ```bash
    # Most likely required
    AUGUR_DB_USER
    AUGUR_DB_PASS
    AUGUR_DB_HOST
    AUGUR_DB_PORT
    AUGUR_DB_NAME

    # Optional
    AUGUR_HOST
    AUGUR_PORT
    AUGUR_PUBLIC_WWW_API_KEY
    AUGUR_GITHUB_API_KEY
    AUGUR_LIBRARIESIO_API_KEY
    AUGUR_DEBUG
    AUGUR_GHTORRENT_PLUS_USER
    AUGUR_GHTORRENT_PLUS_PASS
    AUGUR_GHTORRENT_PLUS_HOST
    AUGUR_GHTORRENT_PLUS_PORT
    AUGUR_GHTORRENT_PLUS_NAME
    ```

    docker-compose will automatically pass the relevant variables from the local environment to the container.


3.  Build the container with `docker-compose build`
4.  Launch the container with `docker-compose up`



Local Installation (For Development)
-----------------------------------------------------

### Dependencies
- [Anaconda](https://www.anaconda.com/download/)
- [MySQL]/MariaDB or later with the [GHTorrent database](http://ghtorrent.org/)
  - You can use the [MSR14 dataset](http://ghtorrent.org/msr14.html) for testing
- [NodeJS](http://nodejs.org) or newer and `npm`


#### Dependency Installation for Ubuntu

```bash
# Install NodeSource
curl -sL https://deb.nodesource.com/setup_8.x | sudo -E bash -

# Install NodeJS and MariaDB 
sudo apt-get install -y nodejs

# Install Anaconda
curl https://repo.anaconda.com/archive/Anaconda3-5.1.0-Linux-x86_64.sh > Anaconda.sh
chmod +x Anaconda.sh

# You must agree to Anaconda's license terms to proceed
./Anaconda.sh -b
rm Anaconda.sh
```


#### Dependency Installation for OS X

```bash
# Install Homebrew
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

# Install node and mariadb
brew install wget node mariadb

# Install Anaconda
cd ~/Downloads
wget https://repo.anaconda.com/archive/Anaconda3-5.1.0-MacOSX-x86_64.pkg
open Anaconda3-5.1.0-MacOSX-x86_64.pkg
```


### Installation

Clone the repo and install the libraries and tools needed by Augur

```bash
git clone https://github.com/OSSHealth/augur/
cd augur
# Install the Python and Node tools and libraries needed
make install-dev
```

Make sure you have a database user that has select access to the database where you installed [GHTorrent](http://ghtorrent.org/) and all priviledges on another database for Augur.

```sql
CREATE USER 'augur'@'localhost' IDENTIFIED BY 'password';
GRANT SELECT ON ghtorrent.* TO 'augur'@'localhost';

CREATE DATABASE augur;
GRANT ALL PRIVILEDGES ON augur.* TO 'augur'@'localhost';
```

Run `augur` to create an `augur.cfg` file. Edit this file with the the required information. In addition to your database information, you will need a [GitHub](https://developer.github.com/v3/) API Key, [PublicWWW](https://publicwww.com/) API Key, and [LibrariesIO](https://libraries.io/) API Key.

You're ready to rock! To start both the frontend and backend, run:
 ```bash
 make dev
 ```
 
After making your changes, run `make build` to update the docs and frontend before adding them to your staging area.

For futher instructions on how to add to Augur, here are guides to adding an endpoint to the full stack. 

[Dev Guide Part 1](docs/dev-guide-pt1.md) 

[Dev Guide Part 2](docs/dev-guide-pt2.md)

Frontend development guide coming soon!

macOS High Sierra (and possibly older OS X Versions) Errata:
If you check the logs/frontend.log and find that "brunch" was not found: 
```bash
brew install npm
npm install -g brunch
brew install yarn
```

If the logs look good but the webpage at localhost:3333 is empty, it could be that Yarn installed the wrong version of some libraries. In that case:

```bash
cd frontend 
npm install
```

License and Copyright
---------------------
Copyright © 2018 University of Nebraska at Omaha, University of Missouri and CHAOSS Project at the Linux Foundation

Augur is free software: you can redistribute it and/or modify it under the terms of the MIT License as published by the Open Source Initiative. See the file [LICENSE](LICENSE) for more details.

(This work has been funded through the Alfred P. Sloan Foundation)
