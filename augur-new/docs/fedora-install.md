# Some notes on installing Augur on Fedora

```
sudo dnf groupinstall "Development Tools" "Development Libraries"

sudo dnf install postgresql-contrib

sudo yum install gcc openssl-devel bzip2-devel libffi-devel zlib-devel

cd /opt

sudo wget https://www.python.org/ftp/python/3.8.12/Python-3.8.12.tgz

sudo tar xzf Python-3.8.12.tgz

cd Python-3.8.12

sudo ./configure --enable-optimizations

sudo make altinstall

python3.8 -V

python3.8 -m venv augur_env

```

## Known Issue: 
1. `augur backend kill` does not seem to kill the backend processes on Fedora right now. 