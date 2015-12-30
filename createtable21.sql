# MySQL script
# create table for TMP36 readings

USE domotica;

DROP TABLE IF EXISTS tmp36;

CREATE TABLE `tmp36` (
  `sample_time`  datetime,
  `sample_epoch` int(11) unsigned,
  `raw_value`    decimal(6,2),
  `temperature`  decimal(5,2),
  PRIMARY KEY (`sample_time`)
  ) ENGINE=InnoDB DEFAULT CHARSET=latin1 ;

# retrieve data:
-- mysql -h sql.lan --skip-column-names -e "USE domotica; SELECT * FROM tmp36 where (sample_time) >=NOW() - INTERVAL 6 HOUR;" | sed 's/\t/;/g;s/\n//g' > /tmp/sql.csv
