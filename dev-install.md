Local Installation (For Development)
-----------------------------------------------------

### Dependencies (OS Specific Instructions Below)
- [Anaconda](https://www.anaconda.com/download/)
- [NodeJS](http://nodejs.org) or newer and `npm`

<a name="Ubuntu">Ubuntu Dependency Installation Instructions</a>

<a name="MacOSX">Mac OSX Dependency Installation Instructions</a>

<a name="Install">Augur Installation Instructions</a>

*Also remember the database dependency in the README.md file* 

[#### Dependency Installation for Ubuntu](#Ubuntu)

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


[#### Dependency Installation for OS X](#MacOSX)

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


[### Installation](#Install)

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