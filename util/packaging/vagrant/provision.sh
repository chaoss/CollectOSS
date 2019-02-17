
# sudo su -

# echo "Updating apt-get..."
# sudo apt-get update

# echo "Installing MariaDB..."
# sudo apt-get install -y mariadb-server

# echo "Creating databases..."
# sudo service mysql restart
# sudo mysql -u root -e 'CREATE DATABASE facade;'
# sudo mysql -u root -e 'CREATE DATABASE msr14;'
# sudo mysql -u root -e 'CREATE DATABASE ghtorrent;'

# echo "Installing NodeSource..."
# curl -sL https://deb.nodesource.com/setup_8.x | sudo -E bash -

# echo "Installing node.js..."
# sudo apt-get install -y nodejs

# echo "Installing pip..."
# sudo apt-get install -y python-pip

sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt-get update -y
sudo apt-get install python3.7 -y

cd $HOME
rm -rf $HOME/augur/
git clone https://github.com/chaoss/augur.git
git checkout vagrant
cd augur

export AUGUR_PYTHON=python3.7
export AUGUR_PIP=pip3

$AUGUR_PIP install -U -e .

# echo "Done!"

