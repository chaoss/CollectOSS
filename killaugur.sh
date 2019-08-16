ps aux | grep -ie $VIRTUAL_ENV | grep -ie augur |  awk '{print "kill -9 " $2}'
ps aux | grep -ie $VIRTUAL_ENV | grep -ie bin | grep worker  |  awk '{print "kill -9 " $2}'
