#!/bin/bash

LOCAL=$(date)
LOCALSECONDS=$(date -d "$LOCAL" +%s)
UTC=$(date -u -d "$LOCAL" +"%Y-%m-%d %H:%M:%S")  #remove timezone reference
UTCSECONDS=$(date -d "$UTC" +%s)
UTCOFFSET=$(($LOCALSECONDS-$UTCSECONDS))

interval="INTERVAL 25 HOUR "

pushd $HOME/bonediagd
  mysql -h sql.lan --skip-column-names -e "USE domotica; SELECT * FROM tmp36  where (sample_time) >=NOW() - $interval;" | sed 's/\t/;/g;s/\n//g' > /tmp/sql21.csv
  #mysql -h sql.lan --skip-column-names -e "USE domotica; SELECT * FROM temper where (sample_time) >=NOW() - $interval;" | sed 's/\t/;/g;s/\n//g' > /tmp/sql21b.csv
  mysql -h sql.lan --skip-column-names -e "USE domotica; SELECT * FROM dht22  where (sample_time) >=NOW() - $interval;" | sed 's/\t/;/g;s/\n//g' > /tmp/sql22.csv
  mysql -h sql.lan --skip-column-names -e "USE domotica; SELECT * FROM bmp183 where (sample_time) >=NOW() - $interval;" | sed 's/\t/;/g;s/\n//g' > /tmp/sql23.csv
  #http://www.sitepoint.com/understanding-sql-joins-mysql-database/
  mysql -h sql.lan --skip-column-names -e "USE domotica; SELECT tmp36.sample_time, tmp36.sample_epoch, tmp36.temperature, bmp183.temperature FROM tmp36 INNER JOIN bmp183 ON tmp36.sample_epoch = bmp183.sample_epoch WHERE (sample_time) >=NOW() - $interval;" | sed 's/\t/;/g;s/\n//g' > /tmp/sql24.csv
  gnuplot -e "utc_offset='${UTCOFFSET}'" ./graph21.gp
  gnuplot -e "utc_offset='${UTCOFFSET}'" ./graph22.gp
  gnuplot -e "utc_offset='${UTCOFFSET}'" ./graph23.gp

popd
