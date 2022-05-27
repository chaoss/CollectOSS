#!/usr/bin/bash
source /home/augur/github/virtualenvs/augur-red/bin/activate 
cd /home/augur/github/augur-red
augur backend stop
augur backend kill 
sleep 30
(nohup augur backend start >logs/sean.log 2>logs/sean.err &)  
