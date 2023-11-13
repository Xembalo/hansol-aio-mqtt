CREATE DATABASE IF NOT EXISTS `qhome` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;

CREATE USER `qhome`@`localhost` IDENTIFIED BY 'qhome';

GRANT ALL PRIVILEGES ON `qhome`.* TO `qhome`@`localhost`;

USE `qhome`;

CREATE TABLE `logs` (
  `id` int(10) UNSIGNED NOT NULL,
  `date` datetime NOT NULL,
  `demand` float NOT NULL,
  `feedin` float NOT NULL,
  `consumption` float NOT NULL,
  `battery_percent` float NOT NULL,
  `pv` float NOT NULL,
  `pv1` float NOT NULL,
  `pv2` float NOT NULL,  
  `temperature` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

ALTER TABLE `logs`
  ADD PRIMARY KEY (`id`),
  ADD KEY `date` (`date`);

ALTER TABLE `logs`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT;


CREATE TABLE `daily_logs` (
  `id` int(10) UNSIGNED NOT NULL,
  `date` date NOT NULL,
  `demand_max` float DEFAULT NULL,
  `demand_max_time` datetime DEFAULT NULL,
  `demand_sum` float DEFAULT NULL,
  `feedin_max` float DEFAULT NULL,
  `feedin_max_time` datetime DEFAULT NULL,
  `feedin_sum` float DEFAULT NULL,
  `consumption_max` float DEFAULT NULL,
  `consumption_max_time` datetime DEFAULT NULL,
  `consumption_sum` float DEFAULT NULL,
  `pv_max` float DEFAULT NULL,
  `pv_max_time` datetime DEFAULT NULL,
  `pv_sum` float DEFAULT NULL,
  `battery_percent_min` float DEFAULT NULL,
  `battery_percent_min_time` datetime DEFAULT NULL,
  `battery_percent_max` float DEFAULT NULL,
  `battery_percent_max_time` datetime DEFAULT NULL,
  `temperature_min` float DEFAULT NULL,
  `temperature_min_time` datetime DEFAULT NULL,
  `temperature_max` float DEFAULT NULL,
  `temperature_max_time` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

ALTER TABLE `daily_logs`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `date` (`date`) USING BTREE;

ALTER TABLE `daily_logs`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT;


CREATE TABLE `monthly_logs` (
  `id` int(10) UNSIGNED NOT NULL,
  `period` varchar(7) NOT NULL COMMENT 'YYYY-MM',
  `demand` float DEFAULT NULL,
  `feedin` float DEFAULT NULL,
  `consumption` float DEFAULT NULL,
  `pv` float DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

ALTER TABLE `monthly_logs`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `period` (`period`) USING BTREE;

ALTER TABLE `monthly_logs`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT;


CREATE TABLE `weekly_logs` (
  `id` int(10) UNSIGNED NOT NULL,
  `period` varchar(7) NOT NULL COMMENT 'YYYY-Week',
  `demand` float DEFAULT NULL,
  `feedin` float DEFAULT NULL,
  `consumption` float DEFAULT NULL,
  `pv` float DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

ALTER TABLE `weekly_logs`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `period` (`period`) USING BTREE;

ALTER TABLE `weekly_logs`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT;


CREATE TABLE `yearly_logs` (
  `id` int(10) UNSIGNED NOT NULL,
  `year` smallint(5) UNSIGNED NOT NULL,
  `demand` float DEFAULT NULL,
  `feedin` float DEFAULT NULL,
  `consumption` float DEFAULT NULL,
  `pv` float DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

ALTER TABLE `yearly_logs`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `year` (`year`) USING BTREE;

ALTER TABLE `yearly_logs`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT;

DELIMITER $$
CREATE TRIGGER `update_stats` BEFORE INSERT ON `logs`
 FOR EACH ROW BEGIN
    INSERT INTO `daily_logs` (
        `date`, 
        `demand_max`, `demand_max_time`, `demand_sum`, 
        `feedin_max`, `feedin_max_time`, `feedin_sum`, 
        `consumption_max`, `consumption_max_time`, `consumption_sum`, 
        `pv_max`, `pv_max_time`, `pv_sum`, 
        `battery_percent_min`, `battery_percent_min_time`, 
        `battery_percent_max`, `battery_percent_max_time`, 
        `temperature_min`, `temperature_min_time`, 
        `temperature_max`, `temperature_max_time`
    ) VALUES (
        date(NEW.`date`), 
        NEW.`demand`, NEW.`date`, NEW.`demand`, 
        NEW.`feedin`, NEW.`date`, NEW.`feedin`, 
        NEW.`consumption`, NEW.`date`, NEW.`consumption`, 
        (NEW.`pv1` + NEW.`pv2`), NEW.`date`, (NEW.`pv1` + NEW.`pv2`), 
        NEW.`battery_percent`, NEW.`date`, 
        NEW.`battery_percent`, NEW.`date`, 
        NEW.`temperature`, NEW.`date`, 
        NEW.`temperature`, NEW.`date`
    ) ON DUPLICATE KEY UPDATE 
        `demand_max`               = IF(NEW.`demand` > IFNULL(`demand_max`, 0), NEW.`demand`, IFNULL(`demand_max`, 0)), 
        `demand_max_time`          = IF(NEW.`demand` > IFNULL(`demand_max`, 0), NEW.`date`, IFNULL(`demand_max_time`,NEW.`date`)),
        `demand_sum`               = IFNULL(`demand_sum`,0) + NEW.`demand`, 
        `feedin_max`               = IF(NEW.`feedin` > IFNULL(`feedin_max`, 0), NEW.`feedin`, IFNULL(`feedin_max`, 0)), 
        `feedin_max_time`          = IF(NEW.`feedin` > IFNULL(`feedin_max`, 0), NEW.`date`, IFNULL(`feedin_max_time`,NEW.`date`)),
        `feedin_sum`               = IFNULL(`feedin_sum`,0) + NEW.`feedin`, 
        `consumption_max`          = IF(NEW.`consumption` > IFNULL(`consumption_max`, 0), NEW.`consumption`, IFNULL(`consumption_max`, 0)), 
        `consumption_max_time`     = IF(NEW.`consumption` > IFNULL(`consumption_max`, 0), NEW.`date`, IFNULL(`consumption_max_time`,NEW.`date`)),
        `consumption_sum`          = IFNULL(`consumption_sum`,0) + NEW.`consumption`, 
        `pv_max`                   = IF((NEW.`pv1` + NEW.`pv2`) > IFNULL(`pv_max`, 0), (NEW.`pv1` + NEW.`pv2`), IFNULL(`pv_max`, 0)), 
        `pv_max_time`              = IF((NEW.`pv1` + NEW.`pv2`) > IFNULL(`pv_max`, 0), NEW.`date`, IFNULL(`pv_max_time`,NEW.`date`)),
        `pv_sum`                   = IFNULL(`pv_sum`,0) + (NEW.`pv1` + NEW.`pv2`),  
        `battery_percent_min`      = IF(NEW.`battery_percent` < IFNULL(`battery_percent_min`, 100), NEW.`battery_percent`, IFNULL(`battery_percent_min`, 100)), 
        `battery_percent_min_time` = IF(NEW.`battery_percent` < IFNULL(`battery_percent_min`, 100), NEW.`date`, IFNULL(`battery_percent_min_time`,NEW.`date`)),
        `battery_percent_max`      = IF(NEW.`battery_percent` > IFNULL(`battery_percent_max`, 0),   NEW.`battery_percent`, IFNULL(`battery_percent_max`, 0)), 
        `battery_percent_max_time` = IF(NEW.`battery_percent` > IFNULL(`battery_percent_max`, 0),   NEW.`date`, IFNULL(`battery_percent_max_time`,NEW.`date`)),
        `temperature_min`          = IF(NEW.`temperature` < IFNULL(`temperature_min`, 100), NEW.`temperature`, IFNULL(`temperature_min`, 100)), 
        `temperature_min_time`     = IF(NEW.`temperature` < IFNULL(`temperature_min`, 100), NEW.`date`, IFNULL(`temperature_min_time`,NEW.`date`)),
        `temperature_max`          = IF(NEW.`temperature` > IFNULL(`temperature_max`, 0),   NEW.`temperature`, IFNULL(`temperature_max`, 0)), 
        `temperature_max_time`     = IF(NEW.`temperature` > IFNULL(`temperature_max`, 0),   NEW.`date`, IFNULL(`temperature_max_time`,NEW.`date`));

    INSERT INTO `weekly_logs` (
        `period`, `demand`, `feedin`, `consumption`, `pv`
    ) VALUES (
        date_format(NEW.`date`, '%x-%v'), NEW.`demand`, NEW.`feedin`, NEW.`consumption`, (NEW.`pv1` + NEW.`pv2`)
    ) ON DUPLICATE KEY UPDATE 
        `demand`               = IFNULL(`demand`,0) + NEW.`demand`, 
        `feedin`               = IFNULL(`feedin`,0) + NEW.`feedin`, 
        `consumption`          = IFNULL(`consumption`,0) + NEW.`consumption`, 
        `pv`                   = IFNULL(`pv`,0) + (NEW.`pv1` + NEW.`pv2`);

    INSERT INTO `monthly_logs` (
        `period`, `demand`, `feedin`, `consumption`, `pv`
    ) VALUES (
        date_format(NEW.`date`, '%Y-%m'), NEW.`demand`, NEW.`feedin`, NEW.`consumption`, (NEW.`pv1` + NEW.`pv2`)
    ) ON DUPLICATE KEY UPDATE 
        `demand`               = IFNULL(`demand`,0) + NEW.`demand`, 
        `feedin`               = IFNULL(`feedin`,0) + NEW.`feedin`, 
        `consumption`          = IFNULL(`consumption`,0) + NEW.`consumption`, 
        `pv`                   = IFNULL(`pv`,0) + (NEW.`pv1` + NEW.`pv2`);

    INSERT INTO `yearly_logs` (
        `year`, `demand`, `feedin`, `consumption`, `pv`
    ) VALUES (
        CAST(date_format(NEW.`date`, '%Y') AS SIGNED), NEW.`demand`, NEW.`feedin`, NEW.`consumption`, (NEW.`pv1` + NEW.`pv2`)
    ) ON DUPLICATE KEY UPDATE 
        `demand`               = IFNULL(`demand`,0) + NEW.`demand`, 
        `feedin`               = IFNULL(`feedin`,0) + NEW.`feedin`, 
        `consumption`          = IFNULL(`consumption`,0) + NEW.`consumption`, 
        `pv`                   = IFNULL(`pv`,0) + (NEW.`pv1` + NEW.`pv2`);
END
$$
DELIMITER ;
