#How to run this:

#Python libraries needed to run this file: Flask, Git Python, SQLAlchemy

#You will need to have Git installed, and it will need to be in your path.
#For example, on Windows you should be able to run a command like 'git pull' from the
#ordinary Windows command prompt and not just from Git Bash.

#You will need a MySQL server with the MSR14 datasource or other GHTorrent database with the same schema.
#Edit the line in this code that says db = sqlalchemy.create_engine to match your username:password@hostname:port/database.

#This file is hardcoded to download the ghdata repository.
#Since it is a preliminary example, each time it runs, 
#it deletes the local ghdata repo and re-downloads it (though this might not be a good option for the future).
#Because of this: if you have a folder named ghdata whose contents you do not want deleted, 
#do not place this file in the same folder as your ghdata folder.

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

#Other issues:
#If a user does not have both an email and organization available in GHTorrent database,
#the user will not be counted towards any organization.

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
    #path is the hardcoded folder for the last download of ghdata
    repo_path = './ghdata'
    #We must remove the old ghdata if we want to download a new copy.
    #In order to delete it, we must first change the permissions
    #To be writable for all files and directories.
    #Based on this: http://stackoverflow.com/questions/2853723/whats-the-python-way-for-recursively-setting-file-permissions
    if os.path.exists(repo_path):
        for root, directories, files in os.walk(repo_path):  
            for directory in directories:  
                os.chmod(os.path.join(root, directory), stat.S_IWRITE)
            for file in files:
                os.chmod(os.path.join(root, file), stat.S_IWRITE)
        os.chmod(repo_path, stat.S_IWRITE)
    
        #delete the old ghdata
        shutil.rmtree(repo_path)
    
    #connect to the database username:password@hostname:port/databasename
    db = sqlalchemy.create_engine('mysql+pymysql://root:password@localhost:3306/msr14')
    schema = sqlalchemy.MetaData()
    schema.reflect(bind=db)
    
    #Get the ghdata repository from GitHub
    repo = Repo.init('ghdata')
    origin = repo.create_remote('origin','https://github.com/OSSHealth/ghdata.git')
    origin.fetch()
    origin.pull(origin.refs[0].remote_head)
    
    #Dictionary to store results of sql queries
    #associating emails with organizations.
    #Without this dictionary, we would have to repeat
    #the same query over and over, which on my local machine
    #meant a runtime of over 24 hours (as opposed to several minutes using the dictionary)
    orgs_associated_with_user = {}
    #This dictionary keeps track of the lines written per organization for a single file.
    lines_per_organization_per_file = {}
    #This is the total number of lines in a single file
    total_lines_in_file = 0
    #this is used later to hold percentage results for output
    percentage = 0
    #This is the total number of lines in an entire repo
    total_lines_in_repo = 0
    #This dictionary keeps track of the lines written per organization for the entire repo.
    lines_per_organization_entire_repo = {}
    
    #The output string will be displayed to the screen once everything is done running.
    outputString = ""
    #Outer loop: loop through each commit in the master branch.
    #This corresponds to the history of commits over time.
    for history_commit in repo.iter_commits('master'):
        #Since we want to see the change over time in repo percentage by organization,
        #clear the variables for total lines and organization lines for each new commit
        #we examine.
        lines_per_organization_entire_repo = {}
        total_lines_in_repo = 0
        #Testing output: only purpose is to show you it's still running :)
        print("Outer loop: " + str(history_commit))
        #Now loop through every file in the repo.
        #You cannot use the os library file/directory loop for this part.
        #(as was used above to change file permissions)
        #That is because some files do not exist in every commit.
        #You must loop through the commit tree, not the ghdata directory.
        for file_in_repo in history_commit.tree.traverse():
            #For each file, we want to clear out the total lines and organization totals per file.
            #That's because we're starting over with a new file.
            lines_per_organization_per_file = {}
            total_lines_in_file = 0
            #Files are of the blob type.  This if statement prevents us from trying
            #to examine 'lines' in a directory.
            if file_in_repo.type == 'blob':
                #Now for each file, perform git blame.  This will traverse
                #the lines in the file.
                #You can see there are now two variables of type commit:
                #history_commit and blame_commit (will improve variable naming in a future update)
                #history_commit is the commit with respect to the overall repo history.
                #blame_commit is the commit in which this line was most recently changed
                #as obtained through git blame.  We use the "blame_commit" variable
                #to obtain the author of the commit for when the lines were last changed.
                for blame_commit, lines in repo.blame(history_commit, file_in_repo.path):
                    #Git blame does not always return one line at a time.
                    #Sometimes we are returned several lines committed by the same author.
                    #In that case, we must count how many lines there are or our
                    #total will not match the actual file.
                    blameLineCount = 0
                    for line in lines:
                        #increment lines to later attribute to an organization.
                        blameLineCount += 1
                        #increment lines in the file as a whole
                        total_lines_in_file += 1
                    #Testing output: only shows that things are still running.
                    print("Inner loop: " + str(blame_commit))
                    #Get the email address of the author of this commit.
                    #If we already have it in our dictionary, increase the total
                    #lines for the associated organization by blameLineCount
                    if blame_commit.author.email in orgs_associated_with_user:
                        for organization in orgs_associated_with_user[blame_commit.author.email]:
                            if organization not in lines_per_organization_per_file:
                                lines_per_organization_per_file[organization] = blameLineCount
                            else:
                                lines_per_organization_per_file[organization] += blameLineCount
                    #If the email address is not in our dictionary, we must query
                    #the database to get any associated organizations.
                    else:
                        sql = text('select orgUser.login as org_name '
                                   'from users as thisUser join organization_members '
                                   'on organization_members.user_id = thisUser.id '
                                   'join users as orgUser on organization_members.org_id = orgUser.id '
                                   'where thisUser.email = "' + blame_commit.author.email + '"')
                        result = db.engine.execute(sql)
                        #add the email to the dictionary
                        orgs_associated_with_user[blame_commit.author.email] = []
                        #if there are organizations in the result, associate those organizations with the
                        #user email in the dictionary.
                        #Then, set or add blameLineCount to the organization total.
                        for organization_row in result:
                            orgs_associated_with_user[blame_commit.author.email] = orgs_associated_with_user[blame_commit.author.email] + [organization_row[0]]
                            if organization_row[0] not in lines_per_organization_per_file:
                                lines_per_organization_per_file[organization_row[0]] = blameLineCount
                            else:
                                lines_per_organization_per_file[organization_row[0]] += blameLineCount
                #If there is at least one line in this file
                if total_lines_in_file > 0:
                    #Add the total lines in this file to the total lines in the repo.
                    total_lines_in_repo += total_lines_in_file
                    #Loop through the organization total lines for this file.
                    #Add each organization to the repo's organization total lines.
                    for organization in lines_per_organization_per_file:
                        if organization not in lines_per_organization_entire_repo:
                            lines_per_organization_entire_repo[organization] = lines_per_organization_per_file[organization]
                        else:
                            lines_per_organization_entire_repo[organization] += lines_per_organization_per_file[organization]
                        #Calculate the percentage for this file by organization (no longer used: former testing output)
                        percentage = lines_per_organization_per_file[organization] / total_lines_in_file * 100
        #Construct output for this commit.  First output the commit, date, and total lines in the repo.
        outputString = outputString + "REPO TOTALS FOR COMMIT: " + str(history_commit) + " authored at " + time.strftime("%I:%M %p, %b %d, %Y", time.gmtime(history_commit.authored_date)) + " <br>" 
        outputString = outputString + "TOTAL REPO LINES: " + str(total_lines_in_repo) + "<br>"
        #Now loop through the organizations and calculate the percentage of the repo for each.
        #Output a line for each organization showing organization name, lines from that organization, percentage of the file
        for organization in lines_per_organization_entire_repo:
            percentage = lines_per_organization_entire_repo[organization] / total_lines_in_repo * 100
            outputString = outputString + " ORGANIZATION: " + str(organization) + " ORG TOTAL LINES: " + str(lines_per_organization_entire_repo[organization]) + " PERCENTAGE OF REPO: " + str(percentage) + "%<br>"
        #Output line between each commit in the history for easier legibility.
        outputString = outputString + "----------------------------------------------------------------------------<br>"
    #Show the outputString in the browser.
    return outputString

if __name__ == "__main__":
    app.run()
