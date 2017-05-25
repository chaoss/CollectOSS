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
if [[ "$DBPASS" != "" ]]
then
  mysql --host=$DBHOST -uroot -p$DBPASS -e "SET GLOBAL sql_mode=(SELECT REPLACE(@@sql_mode,'ONLY_FULL_GROUP_BY','')); DROP DATABASE IF EXISTS msr; CREATE DATABASE msr; CREATE USER 'msr'@'%' IDENTIFIED BY 'msr'; GRANT ALL PRIVILEGES ON msr.* TO 'msr'@'%';"
  zcat msr14-mysql.gz | mysql --host=$DBHOST -umsr -pmsr msr
else
  mysql -uroot --host=$DBHOST -e "SET GLOBAL sql_mode=(SELECT REPLACE(@@sql_mode,'ONLY_FULL_GROUP_BY','')); DROP DATABASE IF EXISTS msr; CREATE DATABASE msr; CREATE USER 'msr'@'%' IDENTIFIED BY 'msr'; GRANT ALL PRIVILEGES ON msr.* TO 'msr'@'%';"
  zcat msr14-mysql.gz | mysql -umsr -pmsr --host=$DBHOST msr
fi
rm msr14-mysql.gz

cat > ghdata.cfg <<ENDCONFIG
[Database]
host = $DBHOST
port = 3306
user = msr
pass = msr
name = msr
ENDCONFIG
echo "ghdata.cfg was generated. New database user 'msr' with password 'msr' was created."
echo "Database installed."
