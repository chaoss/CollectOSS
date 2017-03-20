#How to run this:

#Python libraries needed to run this file: Flask, Git Python, SQLAlchemy

#You will need to have Git installed, and it will need to be in your path.
#For example, on Windows you should be able to run a command like 'git pull' from the
#ordinary Windows command prompt and not just from Git Bash.

#You will need a MySQL server with the MSR14 datasource or other GHTorrent database with the same schema.
#Edit the line in this code that says db = sqlalchemy.create_engine to match your username:password@hostname:port/database.

#This file is hardcoded to download the ghdata repository.
#Since it is a preliminary example, each time it runs, it deletes the local ghdata repo and re-downloads it (though this might not be a good option for the future).
#Because of this: if you have a folder named ghdata whose contents you do not want deleted, do not place this file in the same folder as your ghdata folder.

#to run this, type "python pythonBlameHistoryTree.py" into the command prompt
#You will see some output about running on 127.0.0.1:5000 in the command prompt
#Open a web browser and navigate to 127.0.0.1:5000.
#This page will load for quite a while.  At least several minutes is expected.
#You can see it is still running due to the testing output in the command prompt Outer loop: commit# Inner loop: commit#
#When the testing output stops running you should see some output in the browser tab.

#the output shows the commit number and date, the total lines of code and other files (for example, the readme)
#and the percentage written by each organization.
#expected output for ghdata should show only the spdx-tools organization (Matt is a member)
#Number of lines corresponds to the lines written by Matt.

#You can see that earlier commits are lower on the page, and chronologically later ones appear higher up.

#An "error" I expect us to encounter when testing other repos:
#The way my sql query works right now, a user can be a member of multiple organizations.
#For a simple case of expected output problems:
#User1 wrote the entire repository (100%)
#User1 is a member of Microsoft and IBM
#Microsoft wrote 100% of the repository.  IBM also wrote 100% of the repository for a total of 200%

#Future changes planned for this file:
#Code cleanup for better readability
#Code commenting for each portion
#Thorough testing for various potential cases we might encounter
#Deciding for certain how to decide whether a user is a member of an organization
#A better method of dealing with local repository rather than deleting each time and re-downloading
#Not having the database password directly in the code
#Look into improving code efficiency where possible for faster runtime

from flask import Flask
from git import *
import sqlalchemy
from sqlalchemy import text
import shutil
import os
import stat
import time

app = Flask(__name__)

@app.route("/")
def pythonBlameHistory():
    path = './ghdata'
    if os.path.exists(path):
        for root, directories, files in os.walk(path):  
            for directory in directories:  
                os.chmod(os.path.join(root, directory), stat.S_IWRITE)
            for file in files:
                os.chmod(os.path.join(root, file), stat.S_IWRITE)
        os.chmod(path, stat.S_IWRITE)
    
        shutil.rmtree(path)
    
    db = sqlalchemy.create_engine('mysql+pymysql://root:password@localhost:3306/msr14')
    schema = sqlalchemy.MetaData()
    schema.reflect(bind=db)
    
    repo = Repo.init('ghdata')
    origin = repo.create_remote('origin','https://github.com/OSSHealth/ghdata.git')
    origin.fetch()
    origin.pull(origin.refs[0].remote_head)
    
    emailsAndOrganizations = {}
    organizationTotals = {}
    lineTotal = 0
    percentage = 0
    repoTotalLines = 0
    repoOrganizationTotals = {}
    
    outputString = ""
    for thisCommit in repo.iter_commits('master'):
        repoOrganizationTotals = {}
        repoTotalLines = 0
        print("Outer loop: " + str(thisCommit))
        for entry in thisCommit.tree.traverse():
            organizationTotals = {}
            lineTotal = 0
            if entry.type == 'blob':
                for commit, lines in repo.blame(thisCommit, entry.path):
                    blameLineCount = 0
                    for line in lines:
                        blameLineCount += 1
                        lineTotal += 1
                    print("Inner loop: " + str(commit))
                    if commit.author.email in emailsAndOrganizations:
                        for organization in emailsAndOrganizations[commit.author.email]:
                            if organization not in organizationTotals:
                                organizationTotals[organization] = blameLineCount
                            else:
                                organizationTotals[organization] += blameLineCount
                    else:
                        sql = text('select orgUser.login as org_name '
                                   'from users as thisUser join organization_members '
                                   'on organization_members.user_id = thisUser.id '
                                   'join users as orgUser on organization_members.org_id = orgUser.id '
                                   'where thisUser.email = "' + commit.author.email + '"')
                        result = db.engine.execute(sql)
                        emailsAndOrganizations[commit.author.email] = []
                        for row in result:
                            emailsAndOrganizations[commit.author.email] = emailsAndOrganizations[commit.author.email] + [row[0]]
                            if row[0] not in organizationTotals:
                                organizationTotals[row[0]] = blameLineCount
                            else:
                                organizationTotals[row[0]] += blameLineCount
                if lineTotal > 0:
                    repoTotalLines += lineTotal
                    for key in organizationTotals:
                        if key not in repoOrganizationTotals:
                            repoOrganizationTotals[key] = organizationTotals[key]
                        else:
                            repoOrganizationTotals[key] += organizationTotals[key]
                        percentage = organizationTotals[key] / lineTotal * 100
        outputString = outputString + "REPO TOTALS FOR COMMIT: " + str(thisCommit) + " authored at " + time.strftime("%I:%M %p, %b %d, %Y", time.gmtime(thisCommit.authored_date)) + " <br>" 
        outputString = outputString + "TOTAL REPO LINES: " + str(repoTotalLines) + "<br>"
        for key in repoOrganizationTotals:
            percentage = repoOrganizationTotals[key] / repoTotalLines * 100
            outputString = outputString + " ORGANIZATION: " + str(key) + " ORG TOTAL LINES: " + str(repoOrganizationTotals[key]) + " PERCENTAGE OF REPO: " + str(percentage) + "%<br>"
        outputString = outputString + "----------------------------------------------------------------------------<br>"
    return outputString

if __name__ == "__main__":
    app.run()
