CREATE DATABASE IF NOT EXISTS `qhome` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;

CREATE USER `qhome`@`localhost` IDENTIFIED BY 'qhome';

GRANT ALL PRIVILEGES ON `qhome`.* TO `qhome`@`localhost`;


USE `qhome`;

CREATE TABLE `alerts` (
  `id` int(11) NOT NULL,
  `date` datetime NOT NULL,
  `icon` varchar(255) NOT NULL,
  `message` varchar(1024) NOT NULL,
  `is_read` tinyint(1) NOT NULL,
  `link` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE `logs` (
  `id` int(10) UNSIGNED NOT NULL,
  `date` datetime NOT NULL,
  `demand` float NOT NULL,
  `feedin` float NOT NULL,
  `consumption` float NOT NULL,
  `battery_percent` float NOT NULL,
  `pv` float NOT NULL,
  `temperature` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

ALTER TABLE `alerts`
  ADD PRIMARY KEY (`id`);

ALTER TABLE `logs`
  ADD PRIMARY KEY (`id`),
  ADD KEY `date` (`date`);

ALTER TABLE `alerts`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `logs`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT;

