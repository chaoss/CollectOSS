ps aux | grep -ie augur | grep sean | awk '{print "kill -9 " $2}'

