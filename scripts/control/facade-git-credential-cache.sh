#!/bin/bash

git config --global diff.renames true
git config --global diff.renameLimit 200000
git config --global credential.helper cache
git config --global credential.helper 'cache --timeout=9999999999999'


mkdir /tmp/facade-tmp/
cd /tmp/facade-tmp/

git clone https://github.com/chaoss/augur.git
cd augur
echo "Plase input your Github username and oauth key"
git push