# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure("2") do |config|
  # The most common configuration options are documented and commented below.
  # For a complete reference, please see the online documentation at
  # https://docs.vagrantup.com.

  # Every Vagrant development environment requires a box. You can search for
  # boxes at https://vagrantcloud.com/search.
  config.vm.box = "bento/ubuntu-16.04"
  config.vm.define "augur"
  config.vm.hostname = "augur"

  config.vm.network "forwarded_port", guest: 3333, host: 3333
  config.vm.network "forwarded_port", guest: 5000, host: 5000
  config.vm.synced_folder ".", "/vagrant/augur", type: "rsync", rsync__auto: true, rsync__exclude: ['./node_modules*']

  config.vm.provider "virtualbox" do |v|
    v.name = "augur"
  end

  config.ssh.forward_agent = true

  # documentation for more information about their specific syntax and use.
  config.vm.provision "shell", path: "util/packaging/vagrant/provision.sh"

end
