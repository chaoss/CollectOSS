# augur_sbom_scanner
Goal: This will be a worker. For now, it runs augur-sbom, which is installed separately. 

REMEMBER: Be in your virtual environment. 

## To Run to Gather License Information: 
1. Install `augur-sbom` : `git clone https://github.com/chaoss/augur-sbom`
2. Run `dosocs2 newconfig`
3. Replace contents with augur configuration: 
```
connection_uri = postgresql://user:pasword@host:port/database

schema = spdx

default_scanners = nomos

echo = False

scanner_nomos_path = /usr/local/share/fossology/nomos/agent/nomossa
```
4. Run `python director.py`