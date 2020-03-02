#!/bin/bash

echo "insight worker processes"
ps aux | grep -ie $VIRTUAL_ENV/ | grep -ie bin | grep insight_worker_start  |  awk '{print "kill -9 " $2}'
ps -ef | grep -ie $VIRTUAL_ENV/ | grep -v grep | grep insight_worker_start | awk '{print $2}' | xargs kill
