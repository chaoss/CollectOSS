#!/bin/bash

sudo su -
cd $HOME

echo "Updating apt-get..."
sudo apt-get update

curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash

echo "Installing git-lfs..."
sudo apt-get install git-lfs

echo "Downloadading Facade and GHTorrent datasets..."
git clone https://github.com/augurlabs/vagrant-data.git

echo "Installing MariaDB..."
sudo apt-get install -y mariadb-server
sudo service mysql restart

echo "Creating Facade database..."
sudo mysql -u root -e 'CREATE DATABASE facade;'
sudo mysql -u root -e 'USE facade; source vagrant-data/facade_twitter_dataset.sql;'

echo "Creating GHTorrent database..."
sudo mysql -u root -e 'CREATE DATABASE ghtorrent;'
sudo mysql -u root -e 'USE ghtorrent; source vagrant-data/ghtorrent_minimal.sql;'

echo "Creating Augur user..."
sudo mysql -u root -e 'CREATE USER "augur"@"localhost" IDENTIFIED BY "password"; GRANT SELECT ON facade.* TO "augur"@"localhost"; GRANT SELECT ON ghtorrent.* TO "augur"@"localhost";'

echo "Installing NodeSource..."
curl -sL https://deb.nodesource.com/setup_8.x | sudo -E bash -

echo "Installing node.js..."
sudo apt-get install -y nodejs

echo "Installing pip3..."
sudo apt-get install -y python3-pip

echo "Installing Python3.7..."
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt-get update -y
sudo apt-get install python3.7 -y

echo "Installing IPython..."
sudo apt-get -y install ipython ipython-notebook

cd /vagrant/augur

echo AUGUR_PYTHON=python3.7 >> /etc/environment
echo AUGUR_PIP=pip3 >> /etc/environment
echo "alias pip=pip3" >> /root/.bashrc
source /root/.bashrc

sudo $AUGUR_PIP install -e .

echo "Installing Augur..."
sudo make install-dev

cat vagrant.config.json > augur.config.json

echo "Done!"
