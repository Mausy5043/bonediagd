#!/bin/bash

LOCAL=$(date)
LOCALSECONDS=$(date -d "$LOCAL" +%s)
UTC=$(date -u -d "$LOCAL" +"%Y-%m-%d %H:%M:%S")  #remove timezone reference
UTCSECONDS=$(date -d "$UTC" +%s)
UTCOFFSET=$(($LOCALSECONDS-$UTCSECONDS))

pushd $HOME/bonediagd
  mysql -h sql.lan --skip-column-names -e "USE domotica; SELECT * FROM tmp36 where (sample_time) >=NOW() - INTERVAL 7 DAY;" | sed 's/\t/;/g;s/\n//g' > /tmp/sql21.csv
  mysql -h sql.lan --skip-column-names -e "USE domotica; SELECT * FROM temper where (sample_time) >=NOW() - INTERVAL 7 DAY;" | sed 's/\t/;/g;s/\n//g' > /tmp/sql21b.csv
  gnuplot -e "utc_offset='${UTCOFFSET}'" ./graph21.gp

  mysql -h sql.lan --skip-column-names -e "USE domotica; SELECT * FROM dht22 where (sample_time) >=NOW() - INTERVAL 7 DAY;" | sed 's/\t/;/g;s/\n//g' > /tmp/sql22.csv
  gnuplot -e "utc_offset='${UTCOFFSET}'" ./graph22.gp

popd
