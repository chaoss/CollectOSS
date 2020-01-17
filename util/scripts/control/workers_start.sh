#!/bin/bash


cd workers/facade_worker 
nohup facade_worker_start >f.log 2>f.err &
cd ../..
pwd 

cd workers/github_worker
nohup github_worker_start >gw.log 2>gw.err &
cd ../..
pwd

cd workers/repo_info_worker
nohup repo_info_worker_start >riw.log 2>riw.err &
cd ../..
pwd

cd workers/pull_request_worker
nohup pull_request_worker_start >pr.log 2>pr.err &
cd ../..
pwd

cd workers/linux_badge_worker
nohup linux_badge_worker_start >lbw.log 2>lbw.err &
cd ../..
pwd

cd workers/value_worker
nohup value_worker_start >vw.log 2>vw.err &
cd ../..
pwd

cd workers/insight_worker
nohup insight_worker_start >iw.log 2>iw.err &
cd ../..
pwd
