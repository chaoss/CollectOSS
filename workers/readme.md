# Running Augur Workers

## Steps
1. Start the broker: 
    - `cd augur/augur/broker`
    - `export FLASK_APP=broker/server.py; flask run;`
2. Configure and Install the worker
    - `pip install -e .`
```
        (augur) (base) ➜  linux_badge_worker git:(dev) ✗ pip install -e .   
        Obtaining file:///Volumes/SeansRAIDBaby/github/CHAOSS/augur/workers/linux_badge_worker
        Requirement already satisfied: flask in /Users/gogginsS/augur/lib/python3.6/site-packages (from linux-badge-worker==0.1.0) (1.0.2)
        Requirement already satisfied: requests in /Users/gogginsS/augur/lib/python3.6/site-packages (from linux-badge-worker==0.1.0) (2.18.4)
        Requirement already satisfied: psycopg2-binary in /Users/gogginsS/augur/lib/python3.6/site-packages (from linux-badge-worker==0.1.0) (2.8.2)
        Requirement already satisfied: click in /Users/gogginsS/augur/lib/python3.6/site-packages (from linux-badge-worker==0.1.0) (6.7)
        Requirement already satisfied: Werkzeug>=0.14 in /Users/gogginsS/augur/lib/python3.6/site-packages (from flask->linux-badge-worker==0.1.0) (0.14.1)
        Requirement already satisfied: itsdangerous>=0.24 in /Users/gogginsS/augur/lib/python3.6/site-packages (from flask->linux-badge-worker==0.1.0) (0.24)
        Requirement already satisfied: Jinja2>=2.10 in /Users/gogginsS/augur/lib/python3.6/site-packages (from flask->linux-badge-worker==0.1.0) (2.10)
        Requirement already satisfied: urllib3<1.23,>=1.21.1 in /Users/gogginsS/augur/lib/python3.6/site-packages (from requests->linux-badge-worker==0.1.0) (1.22)
        Requirement already satisfied: chardet<3.1.0,>=3.0.2 in /Users/gogginsS/augur/lib/python3.6/site-packages (from requests->linux-badge-worker==0.1.0) (3.0.4)
        Requirement already satisfied: idna<2.7,>=2.5 in /Users/gogginsS/augur/lib/python3.6/site-packages (from requests->linux-badge-worker==0.1.0) (2.6)
        Requirement already satisfied: certifi>=2017.4.17 in /Users/gogginsS/augur/lib/python3.6/site-packages (from requests->linux-badge-worker==0.1.0) (2018.4.16)
        Requirement already satisfied: MarkupSafe>=0.23 in /Users/gogginsS/augur/lib/python3.6/site-packages (from Jinja2>=2.10->flask->linux-badge-worker==0.1.0) (1.0)
        Installing collected packages: linux-badge-worker
          Running setup.py develop for linux-badge-worker
        Successfully installed linux-badge-worker
        You are using pip version 10.0.1, however version 19.1.1 is available.
        You should consider upgrading via the 'pip install --upgrade pip' command.

```
3. Configure the `augur.config.json` file for the worker. For example, in most cases you will need what is in the `sample.augur.config.json` file only. 
```json 
{   
    "Database": {
        "connection_string": "sqlite:///:memory:",
        "database": "augur",
        "host": "sample.augurlabs.io",
        "pass": "password",
        "port": "5433",
        "schema": "augur_data",
        "user": "augur"
    }
}
```
4. Start the worker:
    - `cd workers/<worker-dir>` 
    - `<worker-name>` for example: `linux_badge_worker`
