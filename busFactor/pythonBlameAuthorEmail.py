#Percentage of code associated with each author email.
#Author email is chosen in place of username because
#not all users have an email in GHTorrent/MSR14

from flask import Flask
from git import *
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
    
    #Get the ghdata repository from GitHub
    repo = Repo.init('ghdata')
    origin = repo.create_remote('origin','https://github.com/OSSHealth/ghdata.git')
    origin.fetch()
    origin.pull(origin.refs[0].remote_head)
    
    #This dictionary keeps track of the lines written per user for a single file.
    lines_per_user_per_file = {}
    #This is the total number of lines in a single file
    total_lines_in_file = 0
    #this is used later to hold percentage results for output
    percentage = 0
    #This is the total number of lines in an entire repo
    total_lines_in_repo = 0
    #This dictionary keeps track of the lines written per user for the entire repo.
    lines_per_user_entire_repo = {}
    
    #The output string will be displayed to the screen once everything is done running.
    outputString = ""
    #Outer loop: loop through each commit in the master branch.
    #This corresponds to the history of commits over time.
    lines_per_user_entire_repo = {}
    total_lines_in_repo = 0
    #Now loop through every file in the repo.
    #You cannot use the os library file/directory loop for this part.
    #(as was used above to change file permissions)
    #That is because some files do not exist in every commit.
    #You must loop through the commit tree, not the ghdata directory.
    for file_in_repo in repo.head.commit.tree.traverse():
        #For each file, we want to clear out the total lines and user totals per file.
        #That's because we're starting over with a new file.
        lines_per_user_per_file = {}
        total_lines_in_file = 0
        #Files are of the blob type.  This if statement prevents us from trying
        #to examine 'lines' in a directory.
        if file_in_repo.type == 'blob':
            for blame_commit, lines in repo.blame('HEAD', file_in_repo.path):
                #Git blame does not always return one line at a time.
                #Sometimes we are returned several lines committed by the same author.
                #In that case, we must count how many lines there are or our
                #total will not match the actual file.
                blameLineCount = 0
                for line in lines:
                    #increment lines to later attribute to an user.
                    blameLineCount += 1
                    #increment lines in the file as a whole
                    total_lines_in_file += 1
                #Testing output: only shows that things are still running.
                print("Inner loop: " + str(blame_commit))
                if blame_commit.author.email not in lines_per_user_per_file:
                    lines_per_user_per_file[blame_commit.author.email] = blameLineCount
                else:
                    lines_per_user_per_file[blame_commit.author.email] += blameLineCount
            #If there is at least one line in this file
            if total_lines_in_file > 0:
                #Add the total lines in this file to the total lines in the repo.
                total_lines_in_repo += total_lines_in_file
                #Loop through the user total lines for this file.
                #Add each user to the repo's user total lines.
                for user in lines_per_user_per_file:
                    if user not in lines_per_user_entire_repo:
                        lines_per_user_entire_repo[user] = lines_per_user_per_file[user]
                    else:
                        lines_per_user_entire_repo[user] += lines_per_user_per_file[user]
                    #Calculate the percentage for this file by user (no longer used: former testing output)
                    percentage = lines_per_user_per_file[user] / total_lines_in_file * 100
    #Construct output for this commit.  First output the commit, date, and total lines in the repo.
    outputString = outputString + "REPO TOTALS FOR COMMIT: " + str(repo.head.commit) + " authored at " + time.strftime("%I:%M %p, %b %d, %Y", time.gmtime(repo.head.commit.authored_date)) + " <br>" 
    outputString = outputString + "TOTAL REPO LINES: " + str(total_lines_in_repo) + "<br>"
    #Now loop through the users and calculate the percentage of the repo for each.
    #Output a line for each user showing user name, lines from that user, percentage of the file
    for user in lines_per_user_entire_repo:
        percentage = lines_per_user_entire_repo[user] / total_lines_in_repo * 100
        outputString = outputString + " user: " + str(user) + " USER TOTAL LINES: " + str(lines_per_user_entire_repo[user]) + " PERCENTAGE OF REPO: " + str(percentage) + "%<br>"
    #Show the outputString in the browser.
    return outputString

if __name__ == "__main__":
    app.run()
