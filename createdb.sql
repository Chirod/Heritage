use mysql;
drop table if exists results, players, registered_users;
CREATE TABLE `players` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `pin` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `u_name` (`first_name`,`last_name`),
  UNIQUE KEY `u_pin` (`pin`)
);

CREATE TABLE `results` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `p1` int(11) DEFAULT NULL,
  `p2` int(11) DEFAULT NULL,
  `p1_w` int(2) DEFAULT NULL,
  `p2_w` int(2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `p1c` (`p1`),
  KEY `p2c` (`p2`),
  CONSTRAINT `p1c` FOREIGN KEY (`p1`) REFERENCES `players` (`id`) ON DELETE CASCADE,
  CONSTRAINT `p2c` FOREIGN KEY (`p2`) REFERENCES `players` (`id`) ON DELETE CASCADE
);

create table registered_users (
`id` int(11) NOT NULL AUTO_INCREMENT,
username varchar(50) not null,
password varchar(50) not null,
primary key (id),
unique key u_user (username)
);
