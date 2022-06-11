#!/bin/bash
cat /home/sean/github/rh/logs/workers/facade_worker/facade_worker_*_collection.log | grep "Processing repo contributors for repo:" | wc -l | mail -s "User Resolution Update from Linda!" s@goggins.com
