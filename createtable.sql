# Below are the commands required to recreate (without data) the table for DHCPNS

USE domotica;

DROP TABLE IF EXISTS tmp36;

CREATE TABLE `tmp36` (
  `sample_time`  datetime,
  `sample_epoch` int(11) unsigned,
  `raw_value`    decimal(6,2),
  `temperature`  decimal(5,2),
  PRIMARY KEY (`sample_time`)
  ) ENGINE=InnoDB DEFAULT CHARSET=latin1 ;
