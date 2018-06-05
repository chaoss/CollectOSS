-- Create Database and Grant Access
create database ghtorrent_blue;
grant all on ghtorrent_blue.* to 'ghtorrent'@'%';
grant all on ghtorrent_blue.* to 'ghtorrent'@'localhost';
grant file on *.* to 'ghtorrent'@'localhost'
