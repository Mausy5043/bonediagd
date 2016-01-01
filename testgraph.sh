#!/bin/bash

LOCAL=$(date)
LOCALSECONDS=$(date -d "$LOCAL" +%s)
UTC=$(date -u -d "$LOCAL" +"%Y-%m-%d %H:%M:%S")  #remove timezone reference
UTCSECONDS=$(date -d "$UTC" +%s)
TIMEZONEGAP=$(($LOCALSECONDS-$UTCSECONDS))

pushd $HOME/bonediagd
  mysql -h sql.lan --skip-column-names -e "USE domotica; SELECT * FROM tmp36 where (sample_time) >=NOW() - INTERVAL 6 HOUR;" | sed 's/\t/;/g;s/\n//g' > /tmp/sql.csv
  gnuplot -e "tz_gap='${TIMEZONEGAP}'" ./graph21.gp
popd
