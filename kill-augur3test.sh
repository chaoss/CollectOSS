ps aux | grep -ie augur3test | grep sean | awk '{print "kill -9 " $2}'

