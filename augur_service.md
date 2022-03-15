## Create a file in the `/etc/systemd/system` directory. Call it `augur.service`, or some equivalent. 

Format it like this, where you provide the full path to the augur_serivce.sh batch file: 
```
[Unit]
Description=Flask Application Augur
After=network.target

[Service]
User=sean
WorkingDirectory=/full/path/to/augur_root
ExecStart=/full/path/to/augur_root/augur_service.sh 

[Install]
WantedBy=multi-user.target
```


