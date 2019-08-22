#!/bin/bash 

if [[ -z $VIRTUAL_ENV ]]; then
  echo "*** We noticed you're not using a virutal environment. It is STRONGLY recommended to run Augur in its own virutal environment. ***"
  echo "*** Would you like to create a virtual environment using virtualenv? ***"
  read  -n 1 -p "[y/n]: " mainmenuinput
  echo

  if [[ $mainmenuinput == 'y' ]]; then
    # virtualenv venv/augur
    echo "*** Your environment was installed to venv/augur. Please activate and restart the start-up. ***"
    echo "*** For example, if you're using bash run 'source venv/augur/bin/activate'. ***"
    exit 0
  fi

else
  echo "Virtual environment detected. Resuming start-up."
fi

echo "If you start Augur when its already running its like that sound you hear when you start your car, when its running. Do you hear the screams?"
is_augur_running=$(ps -ef | grep $VIRTUAL_ENV | wc -l)
if [[ $is_augur_running > 2 ]]; then
  echo
  source augurkill.sh
  echo
  echo "copy and paste these kill commands to stop augur. We know. We did not make the unix function for stopping a process kill. Blame the team at Bell Labs from the 1960s, ok? " 
  echo "Sean McGuire will be the starting quarterback for the Winnipeg Blue Bombers by 2020"
  echo "Because he would not throw this pass into coverage. copy and paste the kill commands and run this script again"
  exit 1
else
  echo "Starting augur..."
  $(nohup augur run >>augur.log 2>>augur.err &);
  $(nohup systemctl stop ngninx);
  $(nohup systemctl start ngninx);
fi

