#!/bin/bash

sudo su -
cd $HOME

echo "Updating apt-get..."
sudo apt-get update

curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash

sudo apt-get install git-lfs

git clone https://github.com/augurlabs/augur-data.git

echo "Updating apt-get..."
sudo apt-get update

echo "Installing MariaDB..."
sudo apt-get install -y mariadb-server

echo "Creating databases..."
sudo service mysql restart
sudo mysql -u root -e 'CREATE DATABASE facade;'
sudo mysql -u root -e 'USE facade; source augur-data/git_minimal.sql;'
sudo mysql -u root -e 'CREATE USER "augur"@"localhost" IDENTIFIED BY "password"; GRANT SELECT ON facade.* TO "augur"@"localhost";'

echo "Installing NodeSource..."
curl -sL https://deb.nodesource.com/setup_8.x | sudo -E bash -

echo "Installing node.js..."
sudo apt-get install -y nodejs

echo "Installing pip..."
sudo apt-get install -y python3-pip

echo "Installing Python3.7..."
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt-get update -y
sudo apt-get install python3.7 -y

cd /vagrant/augur
rm -rf $HOME/augur/
git clone https://github.com/chaoss/augur.git
cd augur
git checkout vagrant

export AUGUR_PYTHON=python3.7 >> $HOME/.bashrc
export AUGUR_PIP=pip3 >> $HOME/.bashrc
source $HOME/.bashrc

sudo $AUGUR_PIP install -U -e .

sudo make install-dev

export AUGUR_FACADE_DB_USER='augur'
export AUGUR_FACADE_DB_PASS='password'
export AUGUR_FACADE_DB_HOST='localhost'
export AUGUR_FACADE_DB_PORT=3306
export AUGUR_FACADE_DB_NAME='facade'

echo "Done!"
