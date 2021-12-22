-- Recurring Table

CREATE TABLE `recurring` (
  `recur_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `payee` varchar(128) NOT NULL,
  `amount` decimal(8,2) NOT NULL,
  `rrule` varchar(512) NOT NULL,
  `start_dt` DATE NOT NULL,
  `memo` varchar(128) DEFAULT NULL,
  `icon` varchar(64) DEFAULT NULL,
  `color` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`recur_id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8;

