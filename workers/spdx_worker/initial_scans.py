#SPDX-License-Identifier: MIT
import subprocess
import psycopg2
from subprocess import PIPE
import json
import re
import os
import requests

def scan(dbname, user, password, host, port, dsfile, ipath):
    connection = psycopg2.connect(
        user = user,
        password = password,
        database = dbname,
        host = host,
        port = port,
    )
    print("********************")
    cur = connection.cursor()
    r = cur.execute("set search_path to augur_data; select repo_path, repo_id, repo_group_id, repo_name from repo order by repo_group_id;")
    rec = cur.fetchall()
    for sector in rec:
        print(sector)
        repo_id = sector[1]
        print("****************")
        print(repo_id)
        cur.execute("set search_path to spdx;")
        cur.execute("select sbom_scan from augur_data.repo_sbom_scans where repo_id = " + str(repo_id) + " LIMIT 1;")
        determin = cur.fetchall()
        if not determin:
            cur.execute("select dosocs_pkg_id from spdx.augur_repo_map where repo_id = " + str(repo_id) + " LIMIT 1;")
            records = cur.fetchall()
            print("****************")
            print("CREATING NEW RECORD")
            path = ipath + str(sector[2]) + "/" + str(sector[0]) + str(sector[3])
            cur.execute("SELECT repo_path FROM spdx.augur_repo_map WHERE" + chr(39) + path + chr(39) + " " + chr(61) + " repo_path;")
            check = bool(cur.rowcount)
            if check == True:
                print("Record Exists in Mapping Table")
            else:
                #Create a new record in "packages" table.
                #dosocs will determine whether the entry has already been made
                print("Creating Record for " + str(sector[1]))
                cur.execute("INSERT INTO spdx.augur_repo_map(repo_id, repo_path) VALUES (" + str(sector[1]) + "," + chr(39) + str(sector[0]) + str(sector[3]) + chr(39) + ");")
                connection.commit()
                #Attempt to create new DoSOCS entry
                print("CREATING NEW DOSOCS DOCUMENT")
                print(path)
                p = subprocess.call(['dosocs2', 'scan', str(path), '-f', 'dosocs2.conf'], shell=False, stdout=PIPE, stderr=PIPE)
                (output) = p
                print("####################")
                print(output)
                print("RECORD CREATED")
        else:
            print("DUPLICATE RECORD FOUND. SKIPPING")
        cur.execute("update augur_repo_map a set dosocs_pkg_name = b.name from packages b where a.repo_path = b.download_location;")
        cur.execute("update augur_repo_map a set dosocs_pkg_id = b.package_id from packages b where a.repo_path = b.download_location;")
    return
