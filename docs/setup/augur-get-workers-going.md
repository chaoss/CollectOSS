# Start up the Augur Workers
1. [Make sure you are still in your python virtual environment, created during setup and installation of Augur.](../installing-augur.md)
2. You will be starting four workers. The first one is the `augur_worker_github`. The configuration in your `augur.config.json` file in Augur root should already be setup from earlier. 
    - From the root of your Augur repository, `cd workers/augur_worker_github`
    - `pip install -e .` installs the worker so you can start it with the command, below. 
    - `nohup github_worker >work.log 2>work.err &` will start the Github Worker that collects issues
    - You can check the log file called `worker.log` to see any output from the worker
    - You can check the log file in the Augur home directory to see any broker errors
    - This worker will populate all `issues` and `contributors` related data associated with the repositories you are monitoring. 
3. Start the `gh_repo_info_worker`. This worker collects repository metadata, including fork counts, star counts and the like.  It stores a record for each repository in your `repos` table for each time it collects data. So, over time, you can see changes in repository statistics. It stores this data in the `repo_info` table, and exposes it through the Augur API. 
    - From the root of your Augur repository, `cd workers/gh_repo_info_worker`
    - `nohup python -m gh_repo_info_worker.runtime >ghinfo.log 2>ghinfo.err &` will start the worker. 
4. Start the `linux_badge_worker`. 
    - From the root of your Augur repository, `cd workers/linux_badge_worker`
    - `pip install -e .` installs the worker so you can start it with the command, below.
    - `nohup linux-badge-worker >work.log 2>work.err &`
5. Start the `facade_worker`. This worker collects all of the commit data for your repositories.  You must have already completed all of the steps in 
    - From the root of your Augur repository, `cd workers/linux_badge_worker`
    - `nohup ./facade00mainprogram.py >facade.log 2>facade.err &` will start the facade worker. 


