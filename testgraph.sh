#!/bin/bash

pushd $HOME/bonediagd
  mysql -h sql.lan --skip-column-names -e "USE domotica; SELECT * FROM tmp36 where (sample_time) >=NOW() - INTERVAL 6 HOUR;" | sed 's/\t/;/g;s/\n//g' > /tmp/sql.csv
  testgraph.gnu
popd
