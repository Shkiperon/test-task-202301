CREATE TABLE `autocalls_tasks` (
  `id` int NOT NULL AUTO_INCREMENT,
  `task_id` varchar(36) NULL,
  `task_created` timestamp NULL,
  `task_stopped` timestamp NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY (`task_id`)
);

CREATE TABLE `autocalls` (
  `id` int NOT NULL AUTO_INCREMENT,
  `task_id` varchar(36),
  `call_created` timestamp NULL,
  `call_number` bigint NULL,
  `call_name` varchar(40),
  `call_status` varchar(128),
  `call_started` timestamp NULL,
  `call_answered` timestamp NULL,
  `call_finished` timestamp NULL,
  FOREIGN KEY (task_id) REFERENCES `autocalls_tasks`(task_id),
  PRIMARY KEY (`id`)
);
