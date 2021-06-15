#!/bin/bash
echo "Removing network interface..."

#Quick compat with macOS
if [ "$(uname -s)" == "Linux" ]
then
    ifconfig lo:0 down
else
    ifconfig lo0 down
fi


#Ask user if they would like to store logs to a permanent file.
#Might want to make where the logs are saved a constant. Right now it just dumps it in the current directory.
read -p "Would you like to store container output in a log file? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
  read -p "Please input log filename: " logFileName
  #Deal with empty user input
  logFileName=${logFileName:-docker}
  
  #Get input up until .
  echo "Logs written to file: "
  echo "$(echo $logFileName | grep -E "^([^.]+)").log"

  #Save log to /var/log/ and delete the /tmp log.
  cat /tmp/dockerComposeLog > "/var/log/$(echo $logFileName | grep -E "^([^.]+)").log"
  echo "/var/log/$logFileName.log has been saved to disk."
  rm /tmp/dockerComposeLog
else
  rm /tmp/dockerComposeLog
fi

