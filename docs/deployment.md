# Production Installation Instructions

These instructions include commands for Ubuntu



## Step 1 - Install dependencies
Before we can begin, we'll need to install the following:
  - MySQL/MariaDB/PerconaDB
  - nginx
  - GNU screen
  - git
  - nodejs 7.x.x or greater
  - make
  - gcc (for native node packages)

  On Ubuntu you can install them using:

  ```bash
  # Install NodeSource repo for more recent versions of NodeJS
  curl -sL https://deb.nodesource.com/setup_8.x | sudo -E bash -
  # Install dependencies
  apt install mariadb-server nginx screen git nodejs make gcc
  ```



## Step 2 - Create ghdata user
You'll want to create a user for the ghdata API server

On Ubuntu:
```bash
useradd ghdata
```



## Step 3 (optional) - Install Anaconda

It is recommended to install [Anaconda](https://www.anaconda.com/download/) to use GHData. If Anaconda is not used, it is recommended to use GHData in a virtual environment. 

First, login as your ghdata user (`su ghdata` if you are root)

Then, to install Anaconda:
```bash
wget https://repo.continuum.io/archive/Anaconda3-4.4.0-Linux-x86_64.sh
chmod +x Anaconda3-4.4.0-Linux-x86_64.sh
./Anaconda3-4.4.0-Linux-x86_64.sh
```

Make sure to add Anaconda to your PATH. There is an option in the installer to add Anaconda to your path automatically. If you did not add Anaconda to your path at install time, you can run this to add it.

```bash
echo "$PATH:$HOME/anaconda/bin" >> ~/.bashrc
```

Make sure to replace `$HOME/anaconda/bin` with the location you installed anaconda, and `.bashrc` with the appropiate `rc` file for your shell.



## Step 4 - Install GHData

First, login as your ghdata user (`su ghdata` if you are root) and download the repo:
```bash
git clone https://github.com/OSSHealth/ghdata
cd ghdata
```

Then, install GHData using `make install`. If you want to help develop GHData, also run `make dev-install`.

