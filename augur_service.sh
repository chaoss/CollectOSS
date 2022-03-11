#!/usr/bin/bash
source /<your_path>/virtualenvs/<your virtualenv>/bin/activate 
cd /home/sean/github/<your augur root>
nohup augur backend start --disable-housekeeper >logs/sean.log 2>logs/sean.err 

