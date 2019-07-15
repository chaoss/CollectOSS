# Start up the Augur Workers
1. [Make sure you are still in your python virtual environment, created during setup and installation of Augur.](../installing-augur.md)
2. You will be starting four workers. The first one is the `augur_worker_github`. The configuration in your `augur.config.json` file in Augur root should already be setup from earlier. 
    - From the root of your Augur repository, `cd workers/augur_worker_github`
    - `nohup github_worker >work.log 2>work.err &` will start the Github Worker that collects issues
    - You can check the log file called `worker.log` to see any output from the worker
    - You can check the log file in the Augur home directory to see any broker errors
    - This worker will populate all `issues` and `contributors` related data associated with the repositories you are monitoring. 
3. 