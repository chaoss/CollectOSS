# Release Notes

## Next Dev to Master Push
1. Schema update script
2. Users may need to create a new virtualenv. Not sure why. I build master then switched to dev and it didn't work until I blew away my virtual environment and recreated it.
3. There are now 2 schema update scripts that I have added to the installer. We need to include a status check for the schema version. 
4. Need to make some notes about postgres configuration for performance on large sets of data
5. Frontend configuration block, which should be an external hostname, and not 0.0.0.0  
```
    "Frontend": {
        "host": "0.0.0.0",
        "port": "5002"
    },
```
6. Put these in the facade worker startup: 
  - `git config --global merge.renameLimit 999999999` lets your facade worker move files when there are large reorganizations in some of your projects
  - Sometimes when a repository moves, github will ask you for credentials. This caches them so your facade worker keeps running 
   - `git config --global credential.helper cache`
   - `git config --global credential.helper 'cache --timeout=600000000000000'`
8. augur-spdx worker block will be needed : 
```
       "license_worker": {
           "port": 59999,
           "switch": 0,
           "workers": 1,
           "tagfile": "3.0.tag"
        }
```
9. Add the housekeeper task for these workers: 
```
            {
                "model": "badges",
                "given": ["git_url"],
                "delay": 150000,
                "repo_group_id": 0
            }


            {
                "model": "value",
                "delay": 100000,
                "given": ["git_url"],
                "repo_group_id": 0
            }
```

## First Collection notes:
1. Run facade worker first. 
2. Run contributors model of github worker (and issues model is ok)
3. Key point: Run facade worker BEFORE the contributors model of the GitHub worker for optimal identity resolution. 

## Server Configuration Notes
1. include nginx instructions
2. include EC2 instructions




