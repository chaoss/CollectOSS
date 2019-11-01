import subprocess
import psycopg2
from subprocess import PIPE
import json
import re
import os
import requests

import sbom_populate as p
import initial_scans as s

if __name__ == "__main__":
    with open("augur_sbom_config.json") as json_file:
        config = json.load(json_file)
        dbname = config["dbname"]
        user = config["user"]
        password = config["password"]
        host = config["host"]
        port = config["port"]
        dsfile = config["dsfile"]
        ipath = config["repos_path"]
        print("---------------------")
        print("INITIAL SCANS RUNNING")
        print("---------------------")
        s.scan(dbname, user, password, host, port, dsfile, ipath)
        print("------------------")
        print("SBOM SCANS RUNNING")
        print("------------------")
        p.scan(dbname, user, password, host, port, dsfile, ipath)
