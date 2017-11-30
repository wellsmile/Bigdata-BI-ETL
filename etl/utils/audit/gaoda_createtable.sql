高达所有表

| card_dec | CREATE TABLE `card_dec` (
  `log_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `role_id` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '角色id',
  `role_level` smallint(8) NOT NULL DEFAULT '0' COMMENT '角色等级',
  `action_type` smallint(8) NOT NULL DEFAULT '0' COMMENT '动作类型',
  `card_id` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '卡牌id',
  `card_level` smallint(6) unsigned NOT NULL DEFAULT '0' COMMENT '卡牌等级',
  `optime` datetime NOT NULL COMMENT '操作时间',
  PRIMARY KEY (`log_id`),
  KEY `roleId` (`role_id`),
  KEY `optime` (`optime`)
) ENGINE=InnoDB AUTO_INCREMENT=12712 DEFAULT CHARSET=utf8 |


| card_get | CREATE TABLE `card_get` (
  `log_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `role_id` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '角色id',
  `role_level` smallint(8) NOT NULL DEFAULT '0' COMMENT '角色等级',
  `action_type` smallint(8) NOT NULL DEFAULT '0' COMMENT '动作类型',
  `card_id` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '卡牌id',
  `card_level` smallint(6) unsigned NOT NULL DEFAULT '0' COMMENT '卡牌等级',
  `optime` datetime NOT NULL COMMENT '操作时间',
  PRIMARY KEY (`log_id`),
  KEY `roleId` (`role_id`),
  KEY `optime` (`optime`)
) ENGINE=InnoDB AUTO_INCREMENT=407430 DEFAULT CHARSET=utf8 |


| energy_change | CREATE TABLE `energy_change` (
  `log_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `role_id` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '角色id',
  `role_level` smallint(8) NOT NULL DEFAULT '0' COMMENT '角色等级',
  `action_type` smallint(8) NOT NULL DEFAULT '0' COMMENT '动作类型',
  `change_type` tinyint(6) NOT NULL DEFAULT '0' COMMENT '变化类型1：增2：减',
  `energy` smallint(6) unsigned NOT NULL DEFAULT '0' COMMENT '变化体力值',
  `now_energy` smallint(6) unsigned NOT NULL DEFAULT '0' COMMENT '当前体力值',
  `optime` datetime NOT NULL COMMENT '操作时间',
  PRIMARY KEY (`log_id`),
  KEY `roleId` (`role_id`),
  KEY `optime` (`optime`)
) ENGINE=InnoDB AUTO_INCREMENT=81876 DEFAULT CHARSET=utf8 |


| equip_dec | CREATE TABLE `equip_dec` (
  `log_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `role_id` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '角色id',
  `role_level` smallint(8) NOT NULL DEFAULT '0' COMMENT '角色等级',
  `action_type` smallint(8) NOT NULL DEFAULT '0' COMMENT '动作类型',
  `equip_basic_id` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '道具id',
  `optime` datetime NOT NULL COMMENT '操作时间',
  PRIMARY KEY (`log_id`),
  KEY `roleId` (`role_id`),
  KEY `optime` (`optime`)
) ENGINE=InnoDB AUTO_INCREMENT=3247 DEFAULT CHARSET=utf8 |


| equip_get | CREATE TABLE `equip_get` (
  `log_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `role_id` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '角色id',
  `role_level` smallint(8) NOT NULL DEFAULT '0' COMMENT '角色等级',
  `action_type` smallint(8) NOT NULL DEFAULT '0' COMMENT '动作类型',
  `equip_basic_id` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '装备配置id',
  `optime` datetime NOT NULL COMMENT '操作时间',
  PRIMARY KEY (`log_id`),
  KEY `roleId` (`role_id`),
  KEY `optime` (`optime`)
) ENGINE=InnoDB AUTO_INCREMENT=12829 DEFAULT CHARSET=utf8 |


| friend_energy | CREATE TABLE `friend_energy` (
  `log_id` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT '流水id',
  `role_id` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '角色id',
  `role_level` smallint(6) unsigned NOT NULL DEFAULT '0' COMMENT '等级',
  `type` tinyint(4) unsigned NOT NULL DEFAULT '0' COMMENT '类型1:赠送2:接收',
  `friend_role_id` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '好友id',
  `friendship` tinyint(4) unsigned NOT NULL DEFAULT '0' COMMENT '友情值',
  `optime` datetime NOT NULL COMMENT '操作时间',
  PRIMARY KEY (`log_id`),
  KEY `role_id` (`role_id`)
) ENGINE=InnoDB AUTO_INCREMENT=16001 DEFAULT CHARSET=utf8 |


| friend_ship | CREATE TABLE `friend_ship` (
  `log_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `role_id` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '角色id',
  `role_level` smallint(8) NOT NULL DEFAULT '0' COMMENT '角色等级',
  `action_type` smallint(8) NOT NULL DEFAULT '0' COMMENT '动作类型',
  `change_type` tinyint(6) NOT NULL DEFAULT '0' COMMENT '变化类型1：增2：减',
  `friendship` smallint(6) unsigned NOT NULL DEFAULT '0' COMMENT '变化友情点',
  `now_friendship` smallint(6) unsigned NOT NULL DEFAULT '0' COMMENT '当前友情点',
  `optime` datetime NOT NULL COMMENT '操作时间',
  PRIMARY KEY (`log_id`),
  KEY `roleId` (`role_id`),
  KEY `optime` (`optime`)
) ENGINE=InnoDB AUTO_INCREMENT=34017 DEFAULT CHARSET=utf8 |


| gem_dec | CREATE TABLE `gem_dec` (
  `log_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `role_id` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '角色id',
  `role_level` smallint(8) NOT NULL DEFAULT '0' COMMENT '角色等级',
  `action_type` smallint(8) NOT NULL DEFAULT '0' COMMENT '动作类型',
  `num` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '消耗个数',
  `totalNum` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '当前个数',
  `optime` datetime NOT NULL COMMENT '操作时间',
  PRIMARY KEY (`log_id`),
  KEY `roleId` (`role_id`),
  KEY `optime` (`optime`)
) ENGINE=InnoDB AUTO_INCREMENT=522334 DEFAULT CHARSET=utf8 |


| gem_get | CREATE TABLE `gem_get` (
  `log_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `role_id` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '角色id',
  `role_level` smallint(8) NOT NULL DEFAULT '0' COMMENT '角色等级',
  `action_type` smallint(8) NOT NULL DEFAULT '0' COMMENT '动作类型',
  `num` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '获得个数',
  `totalNum` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '当前个数',
  `optime` datetime NOT NULL COMMENT '操作时间',
  PRIMARY KEY (`log_id`),
  KEY `roleId` (`role_id`),
  KEY `optime` (`optime`)
) ENGINE=InnoDB AUTO_INCREMENT=17818 DEFAULT CHARSET=utf8 |


| gold_dec | CREATE TABLE `gold_dec` (
  `log_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `role_id` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '角色id',
  `role_level` smallint(8) NOT NULL DEFAULT '0' COMMENT '角色等级',
  `action_type` smallint(8) NOT NULL DEFAULT '0' COMMENT '动作类型',
  `num` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '消耗个数',
  `totalNum` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '当前个数',
  `optime` datetime NOT NULL COMMENT '操作时间',
  PRIMARY KEY (`log_id`),
  KEY `roleId` (`role_id`),
  KEY `optime` (`optime`)
) ENGINE=InnoDB AUTO_INCREMENT=134167 DEFAULT CHARSET=utf8 |


| gold_get | CREATE TABLE `gold_get` (
  `log_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `role_id` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '角色id',
  `role_level` smallint(8) NOT NULL DEFAULT '0' COMMENT '角色等级',
  `action_type` smallint(8) NOT NULL DEFAULT '0' COMMENT '动作类型',
  `num` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '获得个数',
  `totalNum` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '当前个数',
  `optime` datetime NOT NULL COMMENT '操作时间',
  PRIMARY KEY (`log_id`),
  KEY `roleId` (`role_id`),
  KEY `optime` (`optime`)
) ENGINE=InnoDB AUTO_INCREMENT=95270 DEFAULT CHARSET=utf8 |


| item_dec | CREATE TABLE `item_dec` (
  `log_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `role_id` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '角色id',
  `role_level` smallint(8) NOT NULL DEFAULT '0' COMMENT '角色等级',
  `action_type` smallint(8) NOT NULL DEFAULT '0' COMMENT '动作类型',
  `item_id` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '道具id',
  `item_num` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '道具个数',
  `optime` datetime NOT NULL COMMENT '操作时间',
  PRIMARY KEY (`log_id`),
  KEY `roleId` (`role_id`),
  KEY `optime` (`optime`)
) ENGINE=InnoDB AUTO_INCREMENT=150631 DEFAULT CHARSET=utf8 |


| item_get | CREATE TABLE `item_get` (
  `log_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `role_id` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '角色id',
  `role_level` smallint(8) NOT NULL DEFAULT '0' COMMENT '角色等级',
  `action_type` smallint(8) NOT NULL DEFAULT '0' COMMENT '动作类型',
  `item_id` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '道具id',
  `item_num` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '道具个数',
  `optime` datetime NOT NULL COMMENT '操作时间',
  PRIMARY KEY (`log_id`),
  KEY `roleId` (`role_id`),
  KEY `optime` (`optime`)
) ENGINE=InnoDB AUTO_INCREMENT=632911 DEFAULT CHARSET=utf8 |



| newbie_conduct | CREATE TABLE `newbie_conduct` (
  `log_id` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT '流水id',
  `role_id` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '角色id',
  `level` smallint(6) unsigned NOT NULL DEFAULT '0' COMMENT '等级',
  `step` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '步骤',
  `small_step` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '小步骤',
  `optime` datetime NOT NULL COMMENT '操作时间',
  PRIMARY KEY (`log_id`),
  KEY `role_id` (`role_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4636 DEFAULT CHARSET=utf8 |



| pve_result | CREATE TABLE `pve_result` (
  `log_id` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT '流水id',
  `role_id` int(10) unsigned NOT NULL COMMENT '角色id',
  `barrier_id` int(10) unsigned NOT NULL COMMENT '关卡id',
  `event_point` tinyint(4) unsigned NOT NULL COMMENT '关卡点',
  `result` tinyint(4) unsigned NOT NULL COMMENT '结果:1,成功,0,失败',
  `battle_type` tinyint(4) unsigned NOT NULL COMMENT '主线:1,精英:5',
  `user_level` smallint(6) unsigned NOT NULL DEFAULT '0' COMMENT '玩家等级',
  `optime` datetime NOT NULL COMMENT '操作时间',
  PRIMARY KEY (`log_id`),
  KEY `role_id` (`role_id`)
) ENGINE=InnoDB AUTO_INCREMENT=62109 DEFAULT CHARSET=utf8 |


| pvp_result | CREATE TABLE `pvp_result` (
  `log_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `role_id` int(10) NOT NULL DEFAULT '0' COMMENT '玩家id',
  `battle_id` smallint(6) NOT NULL DEFAULT '0' COMMENT '赛次id',
  `scene_id` tinyint(4) NOT NULL DEFAULT '0' COMMENT '场次id',
  `old_ranking` smallint(6) NOT NULL DEFAULT '0' COMMENT '旧排名',
  `cur_ranking` smallint(6) NOT NULL DEFAULT '0' COMMENT '新排名',
  `win_times` tinyint(3) unsigned NOT NULL COMMENT '本轮胜利次数',
  `con_times` smallint(6) unsigned NOT NULL COMMENT '连胜次数',
  `total_times` smallint(6) unsigned NOT NULL COMMENT '累计胜利次数',
  `perfect_times` smallint(6) unsigned NOT NULL COMMENT 'perfect次数',
  `left_ticket` tinyint(4) NOT NULL DEFAULT '0' COMMENT '剩余门票',
  `cur_score` int(10) unsigned NOT NULL COMMENT '当前分数',
  `user_level` smallint(6) unsigned NOT NULL DEFAULT '0' COMMENT '玩家等级',
  `optime` datetime NOT NULL,
  PRIMARY KEY (`log_id`),
  KEY `roleid` (`role_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3659 DEFAULT CHARSET=utf8 |


| role_charge_card | CREATE TABLE `role_charge_card` (
  `log_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `role_id` int(10) NOT NULL DEFAULT '0',
  `optime` datetime NOT NULL,
  `gem` int(10) NOT NULL DEFAULT '0',
  `money` int(10) NOT NULL DEFAULT '0',
  `level` smallint(6) NOT NULL DEFAULT '0',
  `type` tinyint(3) NOT NULL DEFAULT '0',
  PRIMARY KEY (`log_id`),
  KEY `roleid` (`role_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7387 DEFAULT CHARSET=utf8 |


| role_level_up | CREATE TABLE `role_level_up` (
  `log_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `role_id` int(10) NOT NULL DEFAULT '0' COMMENT '玩家id',
  `old_level` smallint(5) unsigned NOT NULL COMMENT '玩家旧等级',
  `level` smallint(5) unsigned NOT NULL COMMENT '玩家当前等级',
  `exp` int(10) unsigned NOT NULL COMMENT '玩家当前经验',
  `levelup_time` int(11) unsigned NOT NULL COMMENT '升级时间',
  `optime` datetime NOT NULL,
  PRIMARY KEY (`log_id`),
  KEY `roleid` (`role_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2517 DEFAULT CHARSET=utf8 |


| role_login_off | CREATE TABLE `role_login_off` (
  `log_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `role_id` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '角色id',
  `level` smallint(8) NOT NULL DEFAULT '0' COMMENT '角色等级',
  `type` tinyint(4) NOT NULL DEFAULT '0' COMMENT '类型1上线2下线',
  `online_time` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '下线时表示在线时长(秒)',
  `optime` datetime NOT NULL COMMENT '操作时间',
  PRIMARY KEY (`log_id`),
  KEY `roleId` (`role_id`),
  KEY `optime` (`optime`)
) ENGINE=InnoDB AUTO_INCREMENT=29281 DEFAULT CHARSET=utf8 |



| role_online_number | CREATE TABLE `role_online_number` (
  `log_id` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT '流水id',
  `channelID` char(32) NOT NULL DEFAULT '' COMMENT 'channelID',
  `online_number` int(10) NOT NULL DEFAULT '0' COMMENT '对应channelID玩家数',
  `line_time` datetime NOT NULL COMMENT '时间点',
  PRIMARY KEY (`log_id`)
) ENGINE=InnoDB AUTO_INCREMENT=18389 DEFAULT CHARSET=utf8 |


| science_point_dec | CREATE TABLE `science_point_dec` (
  `log_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `role_id` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '角色id',
  `role_level` smallint(8) NOT NULL DEFAULT '0' COMMENT '角色等级',
  `action_type` smallint(8) NOT NULL DEFAULT '0' COMMENT '动作类型',
  `num` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '消耗个数',
  `totalNum` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '当前个数',
  `optime` datetime NOT NULL COMMENT '操作时间',
  PRIMARY KEY (`log_id`),
  KEY `roleId` (`role_id`),
  KEY `optime` (`optime`)
) ENGINE=InnoDB AUTO_INCREMENT=2434 DEFAULT CHARSET=utf8 |


| science_point_get | CREATE TABLE `science_point_get` (
  `log_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `role_id` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '角色id',
  `role_level` smallint(8) NOT NULL DEFAULT '0' COMMENT '角色等级',
  `action_type` smallint(8) NOT NULL DEFAULT '0' COMMENT '动作类型',
  `num` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '获得个数',
  `totalNum` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '当前个数',
  `optime` datetime NOT NULL COMMENT '操作时间',
  PRIMARY KEY (`log_id`),
  KEY `roleId` (`role_id`),
  KEY `optime` (`optime`)
) ENGINE=InnoDB AUTO_INCREMENT=213577 DEFAULT CHARSET=utf8 |


