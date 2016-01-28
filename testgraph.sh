#!/bin/bash

LOCAL=$(date)
LOCALSECONDS=$(date -d "$LOCAL" +%s)
UTC=$(date -u -d "$LOCAL" +"%Y-%m-%d %H:%M:%S")  #remove timezone reference
UTCSECONDS=$(date -d "$UTC" +%s)
UTCOFFSET=$(($LOCALSECONDS-$UTCSECONDS))

interval="INTERVAL 25 HOUR "

pushd $HOME/bonediagd
  mysql -h sql.lan --skip-column-names -e "USE domotica; SELECT * FROM temper where (sample_time) >=NOW() - $interval;" | sed 's/\t/;/g;s/\n//g' > /tmp/sql21.csv
  mysql -h sql.lan --skip-column-names -e "USE domotica; SELECT * FROM dht22  where (sample_time) >=NOW() - $interval;" | sed 's/\t/;/g;s/\n//g' > /tmp/sql22.csv
  mysql -h sql.lan --skip-column-names -e "USE domotica; SELECT * FROM bmp183 where (sample_time) >=NOW() - $interval;" | sed 's/\t/;/g;s/\n//g' > /tmp/sql23.csv
  mysql -h sql.lan --skip-column-names -e "USE domotica; SELECT * FROM ds18 where (sample_time) >=NOW() - $interval;" | sed 's/\t/;/g;s/\n//g' > /tmp/sql24.csv
  mysql -h sql.lan --skip-column-names -e "USE domotica; SELECT * FROM tmp36  where (sample_time) >=NOW() - $interval;" | sed 's/\t/;/g;s/\n//g' > /tmp/sql25.csv
  mysql -h sql.lan --skip-column-names -e "USE domotica; SELECT * FROM wind where (sample_time) >=NOW() - INTERVAL 1 MINUTE;" | sed 's/\t/;/g;s/\n//g' > /tmp/sql29.csv

  #http://www.sitepoint.com/understanding-sql-joins-mysql-database/
  mysql -h sql.lan --skip-column-names -e "USE domotica; SELECT ds18.sample_time, ds18.sample_epoch, ds18.temperature, wind.speed FROM ds18 INNER JOIN wind ON ds18.sample_epoch = wind.sample_epoch WHERE (ds18.sample_time) >=NOW() - INTERVAL 1 MINUTE;" | sed 's/\t/;/g;s/\n//g' > /tmp/sql2c.csv
  gnuplot -e "utc_offset='${UTCOFFSET}'" ./graph22.gp
  gnuplot -e "utc_offset='${UTCOFFSET}'" ./graph23.gp
  #gnuplot -e "utc_offset='${UTCOFFSET}'" ./graph24.gp
  gnuplot -e "utc_offset='${UTCOFFSET}'" ./graph25.gp

popd
