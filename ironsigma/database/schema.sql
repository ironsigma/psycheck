-- Recurring Table

CREATE TABLE `recurring` (
  `recur_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `type_code` CHAR (1) NOT NULL CHECK (type_code IN ('D', 'C')),
  `payee` varchar(128) NOT NULL,
  `memo` varchar(128) DEFAULT NULL,
  `amount` decimal(8,2) NOT NULL CHECK (amount > 0),
  `rrule` varchar(512) NOT NULL,
  `start_dt` DATE NOT NULL,
  `icon` varchar(64) DEFAULT NULL,
  `color` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`recur_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;


-- Register Table

CREATE TABLE `register` (
  `reg_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `type_code` CHAR (1) NOT NULL CHECK (type_code IN ('D', 'C', 'd', 'c')),
  `date` DATE NOT NULL,
  `payee` varchar(128) NOT NULL,
  `memo` varchar(128) DEFAULT NULL,
  `amount` decimal(8,2) NOT NULL CHECK (amount > 0),
  `icon` varchar(64) DEFAULT NULL,
  `color` varchar(64) DEFAULT NULL,
  `recur_date` DATE DEFAULT NULL,
  `recur_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`reg_id`),
  KEY `reg_recur_fk` (`recur_id`),
  CONSTRAINT `reg_recur_fk` FOREIGN KEY (`recur_id`)
  REFERENCES `recurring` (`recur_id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
