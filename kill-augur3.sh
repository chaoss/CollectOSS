ps aux | grep -ie augur3 | grep sean | awk '{print "kill -9 " $2}'

