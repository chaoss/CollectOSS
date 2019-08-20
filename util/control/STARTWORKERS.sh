cd workers/linux_badge_worker/
nohup linux-badge-worker >"badge.$(date +%F_%R).log 2>badge.$(date +%F_%R).err" &
cd ../..
cd workers/pull_request_worker/
nohup pull_request_worker_start >"pr.$(date +%F_%R).log 2>pr.$(date +%F_%R).err" &
cd ../..
cd workers/repo_info_worker/
nohup repo_info_worker_start >"riw.$(date +%F_%R).log 2>riw.$(date +%F_%R).err" &
cd ../..
cd workers/metric_status_worker/
nohup metric_stataus_worker_start >"msw.$(date +%F_%R).log 2>msw.$(date +%F_%R).err" &
cd ../..
cd workers/insight_worker/
nohup insight_worker_start >"insight.$(date +%F_%R).log 2>insight.$(date +%F_%R).err" &
cd ../..
