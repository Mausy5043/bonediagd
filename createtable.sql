# Below are the commands required to recreate (without data) the table for DHCPNS

USE domotica;
# mysql> SHOW TABLES;
# +--------------------+
# | Tables_in_dhcpnsdb |
# +--------------------+
# | lantbl             |
# +--------------------+
# 1 row in set (0.00 sec)

# +--------+
# | Table  |
# +--------+
# | lantbl |
# +--------+

CREATE TABLE `tmp36` (
  `sample_time` datetime DEFAULT NOT NULL,
  `sample_epoch` int(11) NOT NULL,
  `raw_value` decimal(6,2) NULL,
  `temperature` decimal(5,2) DEFAULT NULL,
  PRIMARY KEY (`sample_time`)
  ) ENGINE=InnoDB DEFAULT CHARSET=latin1 ;
