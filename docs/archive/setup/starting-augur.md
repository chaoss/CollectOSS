# Starting Augur
1. `augur run` inside your python virtual environment from the augur root directory. 
2. To start the workers, follow these commands: 
	- facade_worker : Clones and collects data
	- github_worker : Collects Github Issue Data
	- gh_repo_info_worker : Collects repository metadata (stars, forks, etc.)
	- linux-badge-worker : Collects any Linux Badging Program data available for a repository (~2,000 such repos are badged, so its usually a small percentage of your projects)
	- gh_pr_worker: Collects information related to GitHub pull requests
	- insight_worker : coming soon!  It is intended to identify anomalies in repository related data (like a 20% increase or decrease in activity [depending on baselines] and be used for providing push notifications.)