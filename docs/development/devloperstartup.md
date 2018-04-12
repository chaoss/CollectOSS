## Detailed installation instructions for Ubuntu

  1. Install Python:

      ```bash
      sudo apt-get install python3-pip
      ```

  2. Clone the repo:

     If you are downloading the official version:

     ```bash
      git clone https://github.com/OSSHealth/augur && cd augur
      ```

     If you are working on your own fork, set the upstream remote:

     ```bash
     git clone https://[yourrepo]/ augur # The repo must be named augur to serve local files
     git remote remove upstream
     git remote add upstream git://github.com/OSSHealth/augur
     ```

     You can then `git fetch` and `git merge upstream/master` to get upstream changes.
     
     One way that is working effectively is to follow the instructions above, then execute the following: 
     
     ```bash
     git pull upstream master
     git push
     ```
     
     This pushes the changes from the parent repository up to the repository you are using on GitHub.  
     Then your teammates can have access to your updates.  Their deployment should be much simpler. 
    
     You also should change the directory name, in this case.  The automated script does this for you if you run it; 
     otherwise, you will need to change the root yourself. 
    
     ```bash
     cd 
     mv [yourrepo] augur
     cd augur
     ```
     For example: 
     
     ```bash
     cd
     mv augur-team39-sprint1 augur
     cd augur
     ```
  
  3. Create a configuration file. The following command will create
     a file augur.cfg suitable for development:

      ```bash
      cat > augur.cfg <<SOFTDEV-CONFIG
      [Server]
      host = 0.0.0.0
      port = 5000

      [Database]
      host = opendata.missouri.edu
      port = 3306
      user = msr
      pass = ghtorrent
      name = msr

      [PublicWWW]
      apikey = 0

      [Development]
      developer = 1
      SOFTDEV-CONFIG
      ```

  4. Install Augur

      ```bash
      sudo pip3 install --upgrade .
      ```

  4. Run:

      ```bash
      augur
      ```
      or, if you want to run it in the background:
      ```
      ~/augur$ nohup augur >augur.log 2>augur.err &
      ```
