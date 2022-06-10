#!/bin/bash
cat logs/workers/facade_worker/facade_worker_*_collection.log | grep "Processing repo contributors for repo:" | wc -l
