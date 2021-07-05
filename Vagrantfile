$script = <<-'SCRIPT'
set -euxo pipefail

sudo apt-get -y update
sudo apt-get -y install --no-install-recommends \
    build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libsqlite3-dev libreadline-dev libffi-dev curl libbz2-dev \
    git gcc gfortran \
    python3 python3-pip python3.8-venv \
    postgresql postgresql-contrib \
    libomp-dev \
    golang libgomp1
sudo pg_ctlcluster 12 main start

go get -u github.com/boyter/scc/

# # install Go
# installGo() (
#     cd "$(mktemp -d)"
#     wget https://golang.org/dl/go1.16.5.linux-amd64.tar.gz
#     rm -rf /usr/local/go && tar -C /usr/local -xzf go1.16.5.linux-amd64.tar.gz
# )
# sudo installGo
# export PATH=$PATH:/usr/local/go/bin


##########################################################################################
# see: https://oss-augur.readthedocs.io/en/master/getting-started/database.html
cat <<EOF > /tmp/init.psql
CREATE DATABASE augur;
CREATE USER augur WITH ENCRYPTED PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE augur TO augur;
EOF
sudo -u postgres psql -U postgres -f /tmp/init.psql


##########################################################################################
# see: https://oss-augur.readthedocs.io/en/master/getting-started/installation.html

mkdir -p "$HOME/augur/" "$HOME/augur/logs/" "$HOME/augur/repos/"
cat <<EOF > "$HOME/augur/config.json"
{
    "Database": {
        "host": "localhost",
        "password": "password"
    },
    "Server": {
        "host": "0.0.0.0"
    },
    "Logging": {
        "logs_directory": "$HOME/augur/logs/",
        "log_level": "INFO",
        "verbose": 0,
        "quiet": 0,
        "debug": 1
    },
    "Workers": {
            "facade_worker": {
                "repo_directory": "$HOME/augur/repos/",
                "switch": 1
            },
            "github_worker": {
                "switch": 1
            },
            "insight_worker": {
                "switch": 1
            },
            "linux_badge_worker": {
                "switch": 1
            },
            "pull_request_worker": {
                "switch": 1
            },
            "repo_info_worker": {
                "switch": 1
            },
            "release_worker": {
                "switch": 1
            }
        }
}
EOF


python3 -m venv $HOME/.virtualenvs/augur_env
source $HOME/.virtualenvs/augur_env/bin/activate
pip install wheel

cd /vagrant
python setup.py bdist_wheel
make clean
make install-dev

augur config init --rc-config-file "$HOME/config.json"
augur db create-schema
augur backend start"

SCRIPT

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/focal64"
	
  config.vm.provider "virtualbox" do |v|
      v.memory = 20480
      v.cpus = 4
  end

  config.vm.provision "shell", privileged: false, inline: $script
end
