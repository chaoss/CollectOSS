echo "augur processes"
ps aux | grep -ie $VIRTUAL_ENV | grep -ie augur |  awk '{print "kill -9 " $2}'
echo "worker processes" 
ps aux | grep -ie $VIRTUAL_ENV | grep -ie bin | grep worker  |  awk '{print "kill -9 " $2}'
