| role_login | CREATE TABLE `role_login` (
  `log_id` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT '??id',
  `role_id` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '????',
  `role_level` smallint(6) unsigned NOT NULL DEFAULT '0' COMMENT '????',
  `role_ip` char(32) NOT NULL DEFAULT '' COMMENT '??ip',
  `gem` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '?????',
  `role_action` tinyint(4) NOT NULL DEFAULT '0' COMMENT '?????0:???1:??',
  `online_time` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '??????(???)',
  `optime` datetime NOT NULL COMMENT '????',
  PRIMARY KEY (`log_id`),
  KEY `key` (`role_id`,`optime`)
) ENGINE=InnoDB AUTO_INCREMENT=274458 DEFAULT CHARSET=utf8 |


| role_gem | CREATE TABLE `role_gem` (
  `log_id` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT '??id',
  `role_id` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '????',
  `role_action` tinyint(4) NOT NULL DEFAULT '0' COMMENT '????,0:??,1:??',
  `gem_source` tinyint(4) NOT NULL DEFAULT '0' COMMENT '????,',
  `gem_old` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '?????',
  `gem_change` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '??????',
  `optime` datetime NOT NULL COMMENT '????',
  PRIMARY KEY (`log_id`),
  KEY `key` (`role_id`,`optime`)
) ENGINE=InnoDB AUTO_INCREMENT=62865 DEFAULT CHARSET=utf8 |


| role_charge | CREATE TABLE `role_charge` (
  `log_id` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT '??id',
  `role_id` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '????',
  `role_level` smallint(6) unsigned NOT NULL DEFAULT '0' COMMENT '????',
  `charge_gem` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '??????',
  `optime` datetime NOT NULL COMMENT '????',
  PRIMARY KEY (`log_id`),
  KEY `key` (`role_id`)
) ENGINE=InnoDB AUTO_INCREMENT=23979 DEFAULT CHARSET=utf8 |
