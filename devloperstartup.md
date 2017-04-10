## Detailed installation instructions for Ubuntu

  1. Install Python:

      ```bash
      sudo apt-get install python3-pip
      ```

  2. Clone the repo:

     If you are downloading the official version:

     ```bash
      git clone https://github.com/OSSHealth/ghdata && cd ghdata
      ```

     If you are working on your own fork, set the upstream remote:

     ```bash
     git clone https://[yourrepo]/ ghdata # The repo must be named ghdata to serve local files
     git remote remove upstream
     git remote add upstream git://github.com/OSSHealth/ghdata
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
     mv [yourrepo] ghdata
     cd ghdata
     ```
     For example: 
     
     ```bash
     cd
     mv ghdata-team39-sprint1 ghdata
     cd ghdata
     ```
  
  3. Create a configuration file. The following command will create
     a file ghdata.cfg suitable for development:

      ```bash
      cat > ghdata.cfg <<SOFTDEV-CONFIG
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

  4. Install GHData

      ```bash
      sudo pip3 install --upgrade .
      ```

  4. Run:

      ```bash
      ghdata
      ```
      or, if you want to run it in the background:
      ```
      ~/ghdata$ nohup ghdata >ghdata.log 2>ghdata.err &
      ```
