Local Installation (For Development)
-----------------------------------------------------

### 1. Install Dependencies (OS Specific Instructions Below)
- Anaconda
- NodeJS Version 8.0 or newer, which includes `npm`

[*Also remember the database dependency in the README.md file*](http://ghtorrent.org/msr14.html)

1. [Dependency Installation for Ubuntu](#Ubuntu) 
1. [Dependency Installation for Fedora](#Fedora)
1. [Dependency Installation for OS X](#MacOSX)

### 2. [Install Augur](#Install)

=====================================================

#### <a name="Ubuntu">Ubuntu Dependency Installation Instructions</a>

```bash
# Install NodeSource
curl -sL https://deb.nodesource.com/setup_8.x | sudo -E bash -

# Install NodeJS
sudo apt-get install -y nodejs

# Install MariaDB (if needed on the same machine for the GHTorrent/msr14 dataset)
sudo apt-get install -y mariadb-server

# Install Anaconda
curl https://repo.anaconda.com/archive/Anaconda3-5.1.0-Linux-x86_64.sh > Anaconda.sh
chmod +x Anaconda.sh

# You must agree to Anaconda's license terms to proceed
./Anaconda.sh -b
rm Anaconda.sh

# [Install Augur](#Install)
```

#### <a name="Fedora">Fedora Dependency Installation Instructions</a>

```bash
# Install NodeSource
curl -sL https://rpm.nodesource.com/setup_10.x | sudo -E bash -
sudo yum install -y nodejs


# Install NodeJS
sudo apt-get install -y nodejs

# Install MariaDB (if needed on the same machine for the GHTorrent/msr14 dataset)
sudo apt-get install -y mariadb-server

# Install Anaconda
curl https://repo.anaconda.com/archive/Anaconda3-5.1.0-Linux-x86_64.sh > Anaconda.sh
chmod +x Anaconda.sh

# You must agree to Anaconda's license terms to proceed
./Anaconda.sh -b
rm Anaconda.sh

# [Install Augur](#Install)
```


#### <a name="MacOSX">Mac OSX Dependency Installation Instructions</a>

```bash
# Install Homebrew
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

# Install NodeJS 
brew install wget node

# Install MariaDB (if needed on the same machine for the GHTorrent/msr14 dataset)
brew install wget mariadb

# Install Anaconda
cd ~/Downloads
wget https://repo.anaconda.com/archive/Anaconda3-5.1.0-MacOSX-x86_64.pkg
open Anaconda3-5.1.0-MacOSX-x86_64.pkg

# [Install Augur](#Install)
```


## <a name="Install">Augur Installation Instructions</a>

Clone the repo and install the libraries and tools needed by Augur

```bash
git clone https://github.com/OSSHealth/augur/

## Assume you are in the root from which you cloned augur

cd augur  ## To get into the project directory root

cd augur ## To get into the augur directory under the augur root, where the make files live

# If you are going to do active development, please use the dev branch
git checkout dev


# Install the Python and Node tools and libraries needed
make install-dev-admin # some libraries require a root install.  

# Ignore node-pre-gyp install errors asking for cairo library or install cairo library. Augur works either way. 

```

**Make sure you have a database user that has select access to the database where you installed [GHTorrent](http://ghtorrent.org/) and all priviledges on another database for Augur.**

```sql
CREATE USER 'augur'@'localhost' IDENTIFIED BY 'password';
GRANT SELECT ON ghtorrent.* TO 'augur'@'localhost';

CREATE DATABASE augur;
GRANT ALL PRIVILEDGES ON augur.* TO 'augur'@'localhost';
```

**Augur runs in an Anaconda environment. To get started, you need to run 'augur' to create the augur.cfg file**

```bash
conda activate augur
augur
```

Edit the augur.cfg file with the the required information for database and API connections. 

For all the API's and visualiazations to work, you will need to include: 

- A [GitHub](https://developer.github.com/v3/) API Key, 
- A [PublicWWW](https://publicwww.com/) API Key, and 
- A [LibrariesIO](https://libraries.io/) API Key.

You **CAN** get off the ground without those API keys though. 

**You're ready to rock! To start both the frontend and backend, run:**
 ```bash
 make dev
 ```




## macOS High Sierra (and possibly older OS X Versions) Errata:

1. If you check the logs/frontend.log and find that "brunch" was not found: 
    ```bash
    brew install npm
    npm install -g brunch
    brew install yarn
    ```
1. If the logs look good but the webpage at localhost:3333 is empty, it could be that Yarn installed the wrong version of some libraries. In that case:
    ```bash
    cd frontend 
    npm install
    ```
