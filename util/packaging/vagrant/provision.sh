#!/bin/bash
echo "Installing Miniconda..."

MINICONDA_SCRIPT=/tmp/miniconda.sh
curl https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh --output MINICONDA_SCRIPT
echo "Downloaded Miniconda to $MINICONDA_SCRIPT"

chmod +x MINICONDA_SCRIPT
$MINICONDA_SCRIPT -b -p $HOME/anaconda
echo "Miniconda installed to ${HOME}/anaconda"

echo "Installing MariaDB..."
sudo yum install -y mariadb-server

echo "Creating databases..."
sudo systemctl start mariadb
sudo systemctl enable mariadb
mysql -u root -e 'CREATE DATABASE facade;'
mysql -u root -e 'CREATE DATABASE msr14;'
mysql -u root -e 'CREATE DATABASE ghtorrentplus;'