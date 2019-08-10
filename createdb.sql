drop table if exists registered_users, league, results, players;

create table registered_users (
`id` int(11) NOT NULL AUTO_INCREMENT,
username varchar(50) not null,
password varchar(50) not null,
primary key (id),
unique key u_user (username)
);

CREATE TABLE `league` (
	`id` int(11) NOT NULL,
	`pid` int(11) NOT NULL,
	PRIMARY KEY (`id`, `pid`),
	foreign key (pid) references registered_users(id)
);

CREATE TABLE `results` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `p1` int(11) NOT NULL,
  `p2` int(11) NOT NULL,
  `p1_w` int(2) NOT NULL,
  `p2_w` int(2) NOT NULL,
  `league` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `p1c` (`p1`),
  KEY `p2c` (`p2`),
  KEY `league` (`league`),
  CONSTRAINT `p1c` FOREIGN KEY (`p1`) REFERENCES `registered_users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `p2c` FOREIGN KEY (`p2`) REFERENCES `registered_users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `leaguec` FOREIGN KEY (`league`) REFERENCES `league` (`id`) ON DELETE CASCADE
);
