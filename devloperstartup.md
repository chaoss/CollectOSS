## Temporary GHData development deployment instructions

  1. Enter the following commands to download ghdata and set it up:

     ```bash
     sudo apt-get update && sudo apt-get install python3-pip
     git clone https://github.com/OSSHealth/ghdata && cd ghdata
     sudo pip3 install --upgrade .
     ```
  2. Configure ghdata.cfg for the opendata server. 
     This can be done with the following command:
    
      ```bash
     cat > ghdata.cfg <<SOFTDEV-CONFIG
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

  2. Edit [ghdata repo]/frontend/scripts/health-report.js and 
     replace 'http://localhost:5000/' with 'http://[your EC2 hostname]:5000/'

  3. Move the files in frontend to a publicly accessible folder. 

     If you don't have one, you can run  
     
     `screen -S frontend -dm bash -c "cd frontend; python3 -m http.server"` 
         
     and kill it with 
     
     `screen -X -S frontend kill`

  4. Run the following command to start ghdata:
      
      ```bash
      flask run --host 0.0.0.0
      ```
      
      You should be good to go. Visit http://[your EC2 server]:5000/ to make sure everything worked!
