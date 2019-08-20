cd workers/github_worker/
nohup github_worker_start >"ghw.$(date +%F_%R).log 2>ghw.backup.$(date +%F_%R).err" &
cd ../..

