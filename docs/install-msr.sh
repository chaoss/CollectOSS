#!/bin/bash
# msr14 install script

function yes_or_no {
    read -p "$1 [y/n]: " -n 1 -r
  if [[ ! $REPLY =~ ^[Yy]$ ]]
  then
    printf "$2\n"
    return 1
  fi
  echo
  return 0
}

echo -n "Database host [localhost]: "
read DBHOST
DBHOST=${DBHOST:-localhost}
echo -n "root@$DBHOST password [none]: "
read -s DBPASS
DBPASS=${DBPASS:-""}
echo
echo "Downloading MSR14 database dump (105MB)..."
curl -Lk https://ghtstorage.blob.core.windows.net/downloads/msr14-mysql.gz > msr14-mysql.gz
echo "Loading MSR14 dump..."
if [[ "$DBPASS" == "" ]]
then
  mysql --defaults-extra-file=<(printf "[client]\nuser = root\npassword = %s" "$DBPASS") --host=$DBHOST -e 'CREATE DATABASE msr;'
  zcat msr14-mysql.gz | mysql --defaults-extra-file=<(printf "[client]\nuser = root\npassword = %s" "$DBPASS") --host=$DBHOST msr
else
  mysql -uroot --host=$DBHOST -e 'CREATE DATABASE msr;'
  zcat msr14-mysql.gz | mysql -uroot --host=$DBHOST msr
fi
rm msr14-mysql.gz
if yes_or_no "Would you like to create a GHData config file with the root database user information (generally not recommended)?" "To create a config file later on, run ghdata.\nA config file with default parameters will be created automatically. Edit the file with the correct information."
then
  cat > ghdata.cfg <<ENDCONFIG
[Database]
host = $DBHOST
port = 3306
user = root
pass = $DBPASS
name = msr
ENDCONFIG
  echo "ghdata.cfg was created with the information you provided."
fi
echo "Database installed."
