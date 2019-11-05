#!/bin/bash

if [[ "$VIRTUAL_ENV" ]]; then
    echo "Killing augur processes."
     ps aux | grep -ie $VIRTUAL_ENV/ |   awk '{print "kill -9 " $2}'
     ps -ef | grep -ie $VIRTUAL_ENV/ | grep -v grep | awk '{print $2}' | xargs kill

    echo "Killing. worker processes"
     ps aux | grep -ie $VIRTUAL_ENV/ | grep -ie bin | grep worker  |  awk '{print "kill -9 " $2}'
     ps -ef | grep -ie $VIRTUAL_ENV/ | grep -v grep | awk '{print $2}' | xargs kill

    echo "O Burr, O Burr, what hast thou done?"
    echo "Thou hast shooted dead great Hamilton."
    echo "You hid behind a bunch of thistle,"
    echo "And shooted him dead with a great hoss pistol."
    echo "http://boston1775.blogspot.com/2014/07/o-burr-o-burr-what-hast-thou-done.html"
    echo "If Augur were Alexander Hamilton, I guess  you're Aaron Burr.  Augur is killed!"
else
    echo "We noticed you're not in a virtual environment. Please activate your augur virtual environment and run the command again{{."
fi
