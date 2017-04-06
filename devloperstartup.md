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
     git remote remove upstream
     git remote add upstream git://github.com/OSSHealth/ghdata
     ```

     You can then `git fetch` and `git merge upstream/master` to get upstream changes.

  
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