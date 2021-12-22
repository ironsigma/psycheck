-- Account Table

CREATE TABLE `account` (
  `acct_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(128) NOT NULL,
  PRIMARY KEY (`acct_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;


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
  `acc_id` bigint(20) NOT NULL,
  PRIMARY KEY (`recur_id`),
  KEY `recurring_fk` (`acc_id`),
  CONSTRAINT `recurring_fk` FOREIGN KEY (`acc_id`)
  REFERENCES `account` (`acct_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8;

