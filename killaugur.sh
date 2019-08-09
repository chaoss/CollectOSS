ps aux | grep -ie augur3 | grep -v test | grep sean | awk '{print "kill -9 " $2}'

