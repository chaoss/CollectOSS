# Installing NodeJS Locally, without `sudo` Access

**NOTE** The NodeJS community states that installing NodeJS as sudo is safer after version 3, which is where we are at; so this workaround exists to allow you to perform development when you have not been given `sudo` access on the computer you are using. You know, if your sysadmins or laptop people follow Ronald Reagan's edict of "Trust, but lock down everyone's computer"; I think he said "Trust, but verify", but I felt the comment warranted updating. 

Installing software through a package manager is the gold standard for operations ready, professional, field tested and battle hardened open source software. Typically these installations require `sudo` or superuser access. This is confusing for new developers, and frequently leads to a practice of `sudo`'ing' every command because it worked for "X", and I don't have time to waste. 

Down the road you will have weird errors and become confused. 

I like how Python's ecosystem handles these types of issues with virtual environments. NodeJS has a more infrastructure focused philosophy, but there is a workaround for setting up a node environment for your user. I detail the steps below, which you could copy and paste into Ubuntu. Fedora should also work, but I loaned my Fedora laptop to a political science PHD student who is using R instead of Python for large scale data analysis and needs the 64 Gig of RAM on that computer. Logged in as your OS user at a terminal, copy and past the following to get a node implementation that is for you alone and does not require `sudo`. 

```shell
echo 'export PATH=$HOME/local/bin:$PATH' >> ~/.bashrc
. ~/.bashrc
mkdir ~/local
mkdir ~/node-latest-install
cd ~/node-latest-install
curl http://nodejs.org/dist/node-latest.tar.gz | tar xz --strip-components=1
./configure --prefix=~/local
make install # ok, fine, this step probably takes more than 30 seconds...
curl https://www.npmjs.org/install.sh | sh
```