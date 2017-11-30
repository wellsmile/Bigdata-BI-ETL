#coding=utf-8
'''
Created on 2017年4月27日

@author: xiaochengcao
'''
from sql_generate_tool import TableSet

DEFAULT_GROUPING_SETS = [
        ('product_id', 'channel_id'),
        ('product_id', 'server_id'),
        ('product_id', 'channel_id', 'server_id'),
        'product_id',
    ]

ONLY_PRODUCT_GROUPING_SETS = ['product_id']

DEFAULT_ANALYSIS_DIMENSIONS = ['product_id',
                                   'channel_id',
                                   'server_id']
    
ONLY_PRODUCT_ANALYSIS_DIMENSIONS = ['product_id']
    
ALL_ANALYSIS = []

# 日活跃用户数据集
ACTIVE_USER_DAILY = TableSet(source_table='matrix_domain')
ACTIVE_USER_DAILY.add_core_dimension('product_id', 'get_json_object(data, \'$.matrix_sdk_context.matrix_token\')',
                                     '产品ID')
ACTIVE_USER_DAILY.add_core_dimension('channel_id', 'get_json_object(data, \'$.context.channel_id\')', '渠道ID')
ACTIVE_USER_DAILY.add_core_dimension('server_id', 'get_json_object(data, \'$.context.server_id\')', '服务器ID')
ACTIVE_USER_DAILY.add_core_dimension('ip', 
                                     '(CASE WHEN get_json_object(data, \'$.matrix_sdk_context.ip\') IS NOT NULL THEN get_json_object(data, \'$.matrix_sdk_context.ip\') WHEN get_json_object(data, \'$.context.ip\') IS NOT NULL THEN get_json_object(data, \'$.context.ip\') ELSE NULL END)',
                                    '用户IP')
ACTIVE_USER_DAILY.add_core_dimension('ds', 'part', '分区日期')
ACTIVE_USER_DAILY.add_core_dimension('role_id', 'get_json_object(data, \'$.context.role_id\')', '角色ID')
ACTIVE_USER_DAILY.add_core_dimension('user_id', 'get_json_object(data, \'$.context.user_id\')', '用户ID')
ACTIVE_USER_DAILY.add_core_dimension('event', 'get_json_object(data, \'$.event\')', '事件名')
ACTIVE_USER_DAILY.add_core_dimension('domain', 'domain', '数据领域')
ACTIVE_USER_DAILY.add_core_filter('domain', 'equal', 'user_rawdata')
ACTIVE_USER_DAILY.add_core_filter('ds', 'equal', '{computation_ds}')

# 日活跃相关分析
daily_active_analysis = ACTIVE_USER_DAILY.copy()

daily_active_analysis.add_analysis_metric('dau', 'user_id', '日活跃独立用户数', 'COUNT_DISTINCT')
daily_active_analysis.add_analysis_metric('dar', 'role_id', '日活跃独立角色数', 'COUNT_DISTINCT')
daily_active_analysis.add_analysis_metric('dai', 'ip', '日独立IP数', 'COUNT_DISTINCT')

daily_active_analysis.add_analysis_output_const('ds', '{computation_ds}')
[daily_active_analysis.add_analysis_dimension(item) for item in DEFAULT_ANALYSIS_DIMENSIONS]
[daily_active_analysis.add_analysis_grouping_set(item) for item in DEFAULT_GROUPING_SETS]

ALL_ANALYSIS.append(daily_active_analysis)
# print (daily_active_analysis.analysis_sql())



# 周活跃用户数据集
ACTIVE_USER_WEEKLY = ACTIVE_USER_DAILY.copy()
ACTIVE_USER_WEEKLY.remove_core_filter('ds')
ACTIVE_USER_WEEKLY.add_core_filter('ds', 'between_function', 
                                   ['DATE_SUB(\'{computation_ds}\', 7)','DATE_SUB(\'{computation_ds}\', 0)'])
# 周活跃相关分析
weekly_active_analysis = ACTIVE_USER_WEEKLY.copy()

weekly_active_analysis.add_analysis_metric('wau', 'user_id', '周活跃用户数', 'COUNT_DISTINCT')
weekly_active_analysis.add_analysis_metric('war', 'role_id', '周活跃角色数', 'COUNT_DISTINCT')
weekly_active_analysis.add_analysis_metric('wai', 'ip', '周独立IP数', 'COUNT_DISTINCT')

weekly_active_analysis.add_analysis_output_const('ds', '{computation_ds}')
[weekly_active_analysis.add_analysis_dimension(item) for item in DEFAULT_ANALYSIS_DIMENSIONS]
[weekly_active_analysis.add_analysis_grouping_set(item) for item in DEFAULT_GROUPING_SETS]

ALL_ANALYSIS.append(weekly_active_analysis)
# print (weekly_active_analysis.analysis_sql())



# 月活跃用户数据集
ACTIVE_USER_MONTHLY = ACTIVE_USER_DAILY.copy()
ACTIVE_USER_MONTHLY.remove_core_filter('ds')
ACTIVE_USER_MONTHLY.add_core_filter('ds',
                                    'between_function',
                                    ['DATE_SUB(\'{computation_ds}\', 30)', 'DATE_SUB(\'{computation_ds}\', 0)'])
monthly_active_analysis = ACTIVE_USER_MONTHLY.copy()

monthly_active_analysis.add_analysis_metric('mau', 'user_id', '月活跃用户数', 'COUNT_DISTINCT')
monthly_active_analysis.add_analysis_metric('mar', 'role_id', '月活跃角色数', 'COUNT_DISTINCT')
monthly_active_analysis.add_analysis_metric('mai', 'ip', '月独立IP数', 'COUNT_DISTINCT')

monthly_active_analysis.add_analysis_output_const('ds', '{computation_ds}')
[monthly_active_analysis.add_analysis_dimension(item) for item in DEFAULT_ANALYSIS_DIMENSIONS]
[monthly_active_analysis.add_analysis_grouping_set(item) for item in DEFAULT_GROUPING_SETS]
ALL_ANALYSIS.append(monthly_active_analysis)
# print (monthly_active_analysis.analysis_sql())



# 活跃留存分析
active_user_last_30days = ACTIVE_USER_DAILY.copy()

active_user_last_30days.remove_core_filter('ds')
active_user_last_30days.add_core_dimension('ds','TO_DATE(get_json_object(data, \'$.context.fixed_time_in_server_tz\'))','活跃时间')
active_user_last_30days.add_core_filter('ds', "between_function",
                                        ["DATE_SUB('{computation_ds}', 30)","DATE_SUB('{computation_ds}', 1)"])

active_user = ACTIVE_USER_DAILY.copy()
active_user.remove_core_filter('ds')
active_user.add_core_dimension('ds','TO_DATE(get_json_object(data, \'$.context.fixed_time_in_server_tz\'))','活跃时间')
active_user.add_core_filter('ds', "equal",'{computation_ds}')


active_retention = active_user_last_30days.intersection(active_user, on=['product_id',
                                                                               'channel_id',
                                                                               'server_id',
                                                                               'user_id'],
                                                                     extra_dimensions=[{
                                                                         'name': 'retention_days',
                                                                         'def': 'DATEDIFF({other_table_alias}.ds, {self_table_alias}.ds)',
                                                                         'display_name': '留存天数'
                                                                     }])   

active_retention_user = active_retention.new_tableset_from_core_sql(as_name = 'T1')

active_retention_user.add_core_dimension('user_id', 'user_id', '用户ID')
active_retention_user.add_core_dimension('channel_id', 'channel_id', '渠道ID')
active_retention_user.add_core_dimension('server_id', 'server_id', '服务器ID')
active_retention_user.add_core_dimension('product_id', 'product_id', '产品ID')
active_retention_user.add_core_dimension('ds', 'ds', '活跃日期')
active_retention_user.add_core_dimension('retention_days', 'retention_days', '留存时间')

# 去掉内部group by
active_retention_user.deduplicate_on_core_dimensions=False

active_retention_user.add_core_filter('retention_days', 'in',('1','7','14','30','60'))

active_retention_user_analysis = active_retention_user.new_tableset_from_core_sql(as_name = 'T2')

active_retention_user_analysis.add_core_dimension('user_id', 'user_id', '用户ID')
active_retention_user_analysis.add_core_dimension('channel_id', 'channel_id', '渠道ID')
active_retention_user_analysis.add_core_dimension('server_id', 'server_id', '服务器ID')
active_retention_user_analysis.add_core_dimension('product_id', 'product_id', '产品ID')
active_retention_user_analysis.add_core_dimension('ds', 'ds', '注册日期')
active_retention_user_analysis.add_core_dimension('retention_days', 'retention_days', '留存时间')

active_retention_user_analysis.add_analysis_metric('daru', 'user_id', '留存人数', 'COUNT_DISTINCT')

# 添加 group by 
active_retention_user_analysis.add_analysis_dimension('ds')
active_retention_user_analysis.add_analysis_dimension('retention_days')
# 添加 grouping_set
active_retention_user_analysis.add_analysis_base_grouping_item('ds')
active_retention_user_analysis.add_analysis_base_grouping_item('retention_days')

[active_retention_user_analysis.add_analysis_dimension(item) for item in DEFAULT_ANALYSIS_DIMENSIONS]
[active_retention_user_analysis.add_analysis_grouping_set(item) for item in DEFAULT_GROUPING_SETS]

ALL_ANALYSIS.append(active_retention_user_analysis)
#print(active_retention_user_analysis.analysis_sql())



# 新增用户累计集合
NEW_USER_DAILY = TableSet(source_table='m2_user_register_detail')
NEW_USER_DAILY.add_core_dimension('user_id', 'user_id', '用户ID')
NEW_USER_DAILY.add_core_dimension('channel_id', 'channel_id', '渠道ID')
NEW_USER_DAILY.add_core_dimension('server_id', 'server_id', '服务器ID')
NEW_USER_DAILY.add_core_dimension('product_id', 'matrix_token', '产品ID')
NEW_USER_DAILY.add_core_dimension('ds', 'to_date(register_time)', '注册日期')
NEW_USER_DAILY.add_core_dimension('part', 'part', '分区日期')
NEW_USER_DAILY.add_core_filter('part', 'equal', '{computation_ds}')
NEW_USER_DAILY.add_core_filter('ds', 'equal', '{computation_ds}')

# 新增用户分析
daily_new_user_analysis = NEW_USER_DAILY.copy()

daily_new_user_analysis.add_analysis_metric('dnu', 'user_id', '日新增用户数', 'COUNT_DISTINCT')

daily_new_user_analysis.add_analysis_output_const('ds', '{computation_ds}')
[daily_new_user_analysis.add_analysis_dimension(item) for item in DEFAULT_ANALYSIS_DIMENSIONS]
[daily_new_user_analysis.add_analysis_grouping_set(item) for item in DEFAULT_GROUPING_SETS]

ALL_ANALYSIS.append(daily_new_user_analysis)
# print(daily_new_user_analysis.analysis_sql())


# 总用户分析
daily_total_user_analysis = NEW_USER_DAILY.copy()
daily_total_user_analysis.add_core_dimension('ds', 'part', '分区时间')
daily_total_user_analysis.add_analysis_metric('dtu', 'user_id', '总用户数', 'COUNT_DISTINCT')

daily_total_user_analysis.add_analysis_output_const('ds', '{computation_ds}')
[daily_total_user_analysis.add_analysis_dimension(item) for item in DEFAULT_ANALYSIS_DIMENSIONS]
[daily_total_user_analysis.add_analysis_grouping_set(item) for item in DEFAULT_GROUPING_SETS]

ALL_ANALYSIS.append(daily_total_user_analysis)
# print(daily_total_user_analysis.analysis_sql())



# 注册留存分析
new_user_last_30days = NEW_USER_DAILY.copy()
new_user_last_30days.remove_core_filter('ds')
new_user_last_30days.add_core_filter('ds', 'between_function',
                                     ["DATE_SUB('{computation_ds}', 30)", "DATE_SUB('{computation_ds}', 1)"])


active_user = ACTIVE_USER_DAILY.copy()
active_user.remove_core_filter('ds')
active_user.add_core_dimension('ds','TO_DATE(get_json_object(data, \'$.context.fixed_time_in_server_tz\'))','活跃时间')
active_user.add_core_filter('ds', "equal",'{computation_ds}')

register_retention = new_user_last_30days.intersection(active_user, on=['product_id',
                                                                                         'channel_id',
                                                                                         'server_id',
                                                                                         'user_id'],
                                                                     extra_dimensions=[{
                                                                         'name': 'retention_days',
                                                                         'def': 'DATEDIFF({other_table_alias}.ds, {self_table_alias}.ds)',
                                                                         'display_name': '留存天数'
                                                                     }])

register_retention_user = register_retention.new_tableset_from_core_sql(as_name = 'T1')

register_retention_user.add_core_dimension('user_id', 'user_id', '用户ID')
register_retention_user.add_core_dimension('channel_id', 'channel_id', '渠道ID')
register_retention_user.add_core_dimension('server_id', 'server_id', '服务器ID')
register_retention_user.add_core_dimension('product_id', 'product_id', '产品ID')
register_retention_user.add_core_dimension('ds', 'ds', '注册日期')
register_retention_user.add_core_dimension('retention_days', 'retention_days', '留存时间')

# 去掉内部group by
register_retention_user.deduplicate_on_core_dimensions=False

register_retention_user.add_core_filter('retention_days', 'in',('1','7','14','30','60','90'))

register_retention_user_analysis = register_retention_user.new_tableset_from_core_sql(as_name = 'T2')

register_retention_user_analysis.add_core_dimension('user_id', 'user_id', '用户ID')
register_retention_user_analysis.add_core_dimension('channel_id', 'channel_id', '渠道ID')
register_retention_user_analysis.add_core_dimension('server_id', 'server_id', '服务器ID')
register_retention_user_analysis.add_core_dimension('product_id', 'product_id', '产品ID')
register_retention_user_analysis.add_core_dimension('ds', 'ds', '注册日期')
register_retention_user_analysis.add_core_dimension('retention_days', 'retention_days', '留存时间')

register_retention_user_analysis.add_analysis_metric('drru', 'user_id', '留存人数', 'COUNT_DISTINCT')

# 添加 group by 
register_retention_user_analysis.add_analysis_dimension('ds')
register_retention_user_analysis.add_analysis_dimension('retention_days')
# 添加 grouping_set
register_retention_user_analysis.add_analysis_base_grouping_item('ds')
register_retention_user_analysis.add_analysis_base_grouping_item('retention_days')

[register_retention_user_analysis.add_analysis_dimension(item) for item in DEFAULT_ANALYSIS_DIMENSIONS]
[register_retention_user_analysis.add_analysis_grouping_set(item) for item in DEFAULT_GROUPING_SETS]

ALL_ANALYSIS.append(register_retention_user_analysis)
# print(register_retention_user_analysis.analysis_sql())



# 新增设备累计集合
NEW_DEVICE_DAILY = TableSet(source_table='m2_device_register')
NEW_DEVICE_DAILY.add_core_dimension('device_id', 'device_id', '设备ID')
NEW_DEVICE_DAILY.add_core_dimension('channel_id', 'channel_id', '渠道ID')
NEW_DEVICE_DAILY.add_core_dimension('server_id', 'server_id', '服务器ID')
NEW_DEVICE_DAILY.add_core_dimension('product_id', 'matrix_token', '产品ID')
NEW_DEVICE_DAILY.add_core_dimension('ds', 'to_date(register_time)', '注册日期')
NEW_DEVICE_DAILY.add_core_dimension('part', 'part', '分区日期')
NEW_DEVICE_DAILY.add_core_filter('part', 'equal', '{computation_ds}')
NEW_DEVICE_DAILY.add_core_filter('ds', 'equal', '{computation_ds}')

# 新增设备分析
daily_new_device_analysis = NEW_DEVICE_DAILY.copy()

daily_new_device_analysis.add_analysis_metric('dnd', 'device_id', '日新增设备数', 'COUNT_DISTINCT')

daily_new_device_analysis.add_analysis_output_const('ds', '{computation_ds}')
[daily_new_device_analysis.add_analysis_dimension(item) for item in DEFAULT_ANALYSIS_DIMENSIONS]
[daily_new_device_analysis.add_analysis_grouping_set(item) for item in DEFAULT_GROUPING_SETS]

ALL_ANALYSIS.append(daily_new_device_analysis)
# print(daily_new_device_analysis.analysis_sql())



# 总设备分析
daily_total_device_analysis = NEW_DEVICE_DAILY.copy()
daily_total_device_analysis.add_core_dimension('ds', 'part', '分区时间')
daily_total_device_analysis.add_analysis_metric('dtd', 'device_id', '总设备数', 'COUNT_DISTINCT')

daily_total_device_analysis.add_analysis_output_const('ds', '{computation_ds}')
[daily_total_device_analysis.add_analysis_dimension(item) for item in DEFAULT_ANALYSIS_DIMENSIONS]
[daily_total_device_analysis.add_analysis_grouping_set(item) for item in DEFAULT_GROUPING_SETS]

ALL_ANALYSIS.append(daily_total_device_analysis)
# print(daily_total_device_analysis.analysis_sql())



# 新增角色累计集合
NEW_ROLE_DAILY = TableSet(source_table='m2_role_register')
NEW_ROLE_DAILY.add_core_dimension('role_id', 'role_id', '角色ID')
NEW_ROLE_DAILY.add_core_dimension('channel_id', 'channel_id', '渠道ID')
NEW_ROLE_DAILY.add_core_dimension('server_id', 'server_id', '服务器ID')
NEW_ROLE_DAILY.add_core_dimension('product_id', 'matrix_token', '产品ID')
NEW_ROLE_DAILY.add_core_dimension('ds', 'to_date(register_time)', '注册日期')
NEW_ROLE_DAILY.add_core_dimension('part', 'part', '分区日期')
NEW_ROLE_DAILY.add_core_filter('part', 'equal', '{computation_ds}')
NEW_ROLE_DAILY.add_core_filter('ds', 'equal', '{computation_ds}')

# 新增角色分析
daily_new_role_analysis = NEW_ROLE_DAILY.copy()

daily_new_role_analysis.add_analysis_metric('dnr', 'role_id', '日新增角色数', 'COUNT_DISTINCT')

daily_new_role_analysis.add_analysis_output_const('ds', '{computation_ds}')
[daily_new_role_analysis.add_analysis_dimension(item) for item in DEFAULT_ANALYSIS_DIMENSIONS]
[daily_new_role_analysis.add_analysis_grouping_set(item) for item in DEFAULT_GROUPING_SETS]

ALL_ANALYSIS.append(daily_new_role_analysis)
# print(daily_new_role_analysis.analysis_sql())



# 付费用户数据集
PAY_USER_DAILY = TableSet(source_table='matrix_domain')
PAY_USER_DAILY.add_core_dimension('product_id', 'get_json_object(data, \'$.matrix_sdk_context.matrix_token\')',
                                     '产品ID')
PAY_USER_DAILY.add_core_dimension('channel_id', 'get_json_object(data, \'$.context.channel_id\')', '渠道ID')
PAY_USER_DAILY.add_core_dimension('server_id', 'get_json_object(data, \'$.context.server_id\')', '服务器ID')
PAY_USER_DAILY.add_core_dimension('amount', 
                                  'COALESCE(get_json_object(data,\'$.context.amount\'),get_json_object(data,\'$.context.amount:\') ,\'0\')',
                                  '支付钱数')
PAY_USER_DAILY.add_core_dimension('ds', 'to_date(get_json_object(data, \'$.context.fixed_time_in_server_tz\'))', '支付时间')
PAY_USER_DAILY.add_core_dimension('part', 'part', '分区时间')
PAY_USER_DAILY.add_core_dimension('role_id', 'get_json_object(data, \'$.context.role_id\')', '角色ID')
PAY_USER_DAILY.add_core_dimension('user_id', 'get_json_object(data, \'$.context.user_id\')', '用户ID')
PAY_USER_DAILY.add_core_dimension('event', 'get_json_object(data, \'$.event\')', '事件名')
PAY_USER_DAILY.add_core_dimension('domain', 'domain', '数据领域')
PAY_USER_DAILY.add_core_filter('domain', 'equal', 'user_rawdata')
PAY_USER_DAILY.add_core_filter('ds', 'equal', '{computation_ds}')
PAY_USER_DAILY.add_core_filter('part', 'equal', '{computation_ds}')
PAY_USER_DAILY.add_core_filter('event', 'equal', 'user pay')

# 付费用户分析
daily_pay_user_analysis = PAY_USER_DAILY.copy()
    
daily_pay_user_analysis.add_analysis_metric('dpu', 'user_id', '日付费用户数', 'COUNT_DISTINCT')
daily_pay_user_analysis.add_analysis_metric('dpr', 'role_id', '日付费角色数', 'COUNT_DISTINCT')

daily_pay_user_analysis.add_analysis_output_const('ds', '{computation_ds}')
[daily_pay_user_analysis.add_analysis_dimension(item) for item in DEFAULT_ANALYSIS_DIMENSIONS]
[daily_pay_user_analysis.add_analysis_grouping_set(item) for item in DEFAULT_GROUPING_SETS]

ALL_ANALYSIS.append(daily_pay_user_analysis)
# print (daily_pay_user_analysis.analysis_sql())


# 付费用户总数
total_pay_user = PAY_USER_DAILY.copy()

total_pay_user.remove_core_filter('part')
total_pay_user.add_core_filter('part', 'lte_function','{computation_ds}')

total_pay_user.remove_core_filter('ds')
total_pay_user.add_core_filter('ds', 'lte_function','{computation_ds}')
total_pay_user.add_analysis_metric('tpu', 'user_id', '付费用户总数', 'COUNT_DISTINCT')
total_pay_user.add_analysis_metric('tpr', 'role_id', '付费角色总数', 'COUNT_DISTINCT')

total_pay_user.add_analysis_output_const('ds', '{computation_ds}')
[total_pay_user.add_analysis_dimension(item) for item in DEFAULT_ANALYSIS_DIMENSIONS]
[total_pay_user.add_analysis_grouping_set(item) for item in DEFAULT_GROUPING_SETS]

ALL_ANALYSIS.append(total_pay_user)

# print (total_pay_user.analysis_sql())


# 日付费额
daily_pay_money_analysis = PAY_USER_DAILY.copy()
# 去掉内部group by
daily_pay_money_analysis.deduplicate_on_core_dimensions=False

daily_pay_money_analysis.add_analysis_metric('dpm', 'amount/100', '日付费额', 'SUM')

daily_pay_money_analysis.add_analysis_output_const('ds', '{computation_ds}')
[daily_pay_money_analysis.add_analysis_dimension(item) for item in DEFAULT_ANALYSIS_DIMENSIONS]
[daily_pay_money_analysis.add_analysis_grouping_set(item) for item in DEFAULT_GROUPING_SETS]

ALL_ANALYSIS.append(daily_pay_money_analysis)
# print (daily_pay_money_analysis.analysis_sql())



# 付费用户留存
pay_user_last_30days = PAY_USER_DAILY.copy()
pay_user_last_30days.remove_core_filter('ds')
pay_user_last_30days.add_core_filter('ds', 'between_function',
                                     ["DATE_SUB('{computation_ds}', 30)", "DATE_SUB('{computation_ds}', 1)"])
pay_user_last_30days.remove_core_filter('part')
pay_user_last_30days.add_core_filter('part', 'between_function',
                                     ["DATE_SUB('{computation_ds}', 30)", "DATE_SUB('{computation_ds}', 1)"])

active_user = ACTIVE_USER_DAILY.copy()
active_user.remove_core_filter('ds')
active_user.add_core_dimension('ds','TO_DATE(get_json_object(data, \'$.context.fixed_time_in_server_tz\'))','活跃时间')
active_user.add_core_filter('ds', "equal",'{computation_ds}')

payment_retention = pay_user_last_30days.intersection(active_user, on=['product_id',
                                                                                       'channel_id',
                                                                                       'server_id',
                                                                                        'user_id'],
                                                                     extra_dimensions=[{
                                                                         'name': 'retention_days',
                                                                         'def': 'DATEDIFF({other_table_alias}.ds, {self_table_alias}.ds)',
                                                                         'display_name': '留存天数'
                                                                     }])

payment_retention_user = payment_retention.new_tableset_from_core_sql(as_name = 'T1')

payment_retention_user.add_core_dimension('user_id', 'user_id', '用户ID')
payment_retention_user.add_core_dimension('channel_id', 'channel_id', '渠道ID')
payment_retention_user.add_core_dimension('server_id', 'server_id', '服务器ID')
payment_retention_user.add_core_dimension('product_id', 'product_id', '产品ID')
payment_retention_user.add_core_dimension('ds', 'ds', '注册日期')
payment_retention_user.add_core_dimension('retention_days', 'retention_days', '留存时间')

# 去掉内部group by
payment_retention_user.deduplicate_on_core_dimensions=False

payment_retention_user.add_core_filter('retention_days', 'in',('1','7','14','30','60'))

payment_retention_user_analysis = payment_retention_user.new_tableset_from_core_sql(as_name = 'T2')

payment_retention_user_analysis.add_core_dimension('user_id', 'user_id', '用户ID')
payment_retention_user_analysis.add_core_dimension('channel_id', 'channel_id', '渠道ID')
payment_retention_user_analysis.add_core_dimension('server_id', 'server_id', '服务器ID')
payment_retention_user_analysis.add_core_dimension('product_id', 'product_id', '产品ID')
payment_retention_user_analysis.add_core_dimension('ds', 'ds', '注册日期')
payment_retention_user_analysis.add_core_dimension('retention_days', 'retention_days', '留存时间')

payment_retention_user_analysis.add_analysis_metric('dpru', 'user_id', '留存人数', 'COUNT_DISTINCT')

# 添加 group by 
payment_retention_user_analysis.add_analysis_dimension('ds')
payment_retention_user_analysis.add_analysis_dimension('retention_days')
# 添加 grouping_set
payment_retention_user_analysis.add_analysis_base_grouping_item('ds')
payment_retention_user_analysis.add_analysis_base_grouping_item('retention_days')

[payment_retention_user_analysis.add_analysis_dimension(item) for item in DEFAULT_ANALYSIS_DIMENSIONS]
[payment_retention_user_analysis.add_analysis_grouping_set(item) for item in DEFAULT_GROUPING_SETS]

ALL_ANALYSIS.append(payment_retention_user_analysis)
# print(payment_retention_user_analysis.analysis_sql())



# 新增即付费用户分析
new_user = NEW_USER_DAILY.copy()
new_user_and_pay = new_user.intersection(PAY_USER_DAILY, on=['product_id',
                                                             'channel_id',
                                                             'server_id',
                                                             'user_id'])

new_user_and_pay.add_analysis_metric('dnp', 'user_id', '新增即付费用户数', 'COUNT_DISTINCT')

new_user_and_pay.add_analysis_output_const('ds', '{computation_ds}')
[new_user_and_pay.add_analysis_dimension(item) for item in DEFAULT_ANALYSIS_DIMENSIONS]
[new_user_and_pay.add_analysis_grouping_set(item) for item in DEFAULT_GROUPING_SETS]

ALL_ANALYSIS.append(new_user_and_pay)
# print (new_user_and_pay.analysis_sql())


# 新增即付费的付费额
new_user_money = NEW_USER_DAILY.copy()

PAY_USER_DAILY.deduplicate_on_core_dimensions=False

new_user_and_pay_money = PAY_USER_DAILY.intersection(new_user_money, on=['product_id',
                                                                         'channel_id',
                                                                         'server_id',
                                                                         'user_id'])
# 去掉内部group by
new_user_and_pay_money.deduplicate_on_core_dimensions=False

new_user_and_pay_money.add_analysis_metric('dnpm', 'amount/100', '新增即付费的付费额', 'SUM')

new_user_and_pay_money.add_analysis_output_const('ds', '{computation_ds}')
[new_user_and_pay_money.add_analysis_dimension(item) for item in DEFAULT_ANALYSIS_DIMENSIONS]
[new_user_and_pay_money.add_analysis_grouping_set(item) for item in DEFAULT_GROUPING_SETS]

ALL_ANALYSIS.append(new_user_and_pay_money)
# print (new_user_and_pay_money.analysis_sql())



# 在线时长集合（没有channel_id,server_id）
DAILY_USER_SESSION = TableSet(source_table='matrix_domain')
DAILY_USER_SESSION.add_core_dimension('product_id', 'get_json_object(data, \'$.matrix_token\')',
                                     '产品ID')
DAILY_USER_SESSION.add_core_dimension('ds', 'part', '分区时间')
DAILY_USER_SESSION.add_core_dimension('user_id', 'get_json_object(data, \'$.user_id\')', '用户ID')
DAILY_USER_SESSION.add_core_dimension('session_seconds', 'get_json_object(data, \'$.session_seconds\')', '用户ID')
DAILY_USER_SESSION.add_core_dimension('domain', 'domain', '数据领域')
DAILY_USER_SESSION.add_core_filter('domain', 'equal', 'user_sessions')
DAILY_USER_SESSION.add_core_filter('ds', 'equal', '{computation_ds}')

# 全部玩家总在线时长
all_user_sessions = DAILY_USER_SESSION.copy()

# 去掉内部group by
all_user_sessions.deduplicate_on_core_dimensions=False

all_user_sessions.add_analysis_metric('duot', 'session_seconds', '全部玩家总在线时长', 'SUM', hook=lambda x: '%.2f' % (x/3600))

all_user_sessions.add_analysis_output_const('ds', '{computation_ds}')
[all_user_sessions.add_analysis_dimension(item) for item in ONLY_PRODUCT_ANALYSIS_DIMENSIONS]
[all_user_sessions.add_analysis_grouping_set(item) for item in ONLY_PRODUCT_GROUPING_SETS]

ALL_ANALYSIS.append(all_user_sessions)
# print (all_user_sessions.analysis_sql())



# 全部玩家总游戏次数
user_game_num = DAILY_USER_SESSION.copy()

# 去掉内部group by
user_game_num.deduplicate_on_core_dimensions=False

user_game_num.add_analysis_metric('snog', 'user_id', '全部玩家总游戏次数', 'COUNT')

user_game_num.add_analysis_output_const('ds', '{computation_ds}')
[user_game_num.add_analysis_dimension(item) for item in ONLY_PRODUCT_ANALYSIS_DIMENSIONS]
[user_game_num.add_analysis_grouping_set(item) for item in ONLY_PRODUCT_GROUPING_SETS]

ALL_ANALYSIS.append(user_game_num)
# print (user_game_num.analysis_sql())



    
# 有效新增
# 有效新增用户累计集合
NEW_USER = TableSet(source_table='m2_user_register')
NEW_USER.add_core_dimension('user_id', 'user_id', '用户ID')
NEW_USER.add_core_dimension('product_id', 'matrix_token', '产品ID')
NEW_USER.add_core_dimension('ds', 'to_date(register_time)', '注册日期')
NEW_USER.add_core_dimension('part', 'part', '分区日期')
NEW_USER.add_core_filter('part', 'equal', '{computation_ds}')
NEW_USER.add_core_filter('ds', 'equal', '{computation_ds}')


outvalue_new_user = DAILY_USER_SESSION.copy()
# 去掉内部group by
outvalue_new_user.deduplicate_on_core_dimensions=False

outvalue_new_user.add_analysis_metric('session_time', 'session_seconds/60', '每个用户的在线时长', 'SUM')

outvalue_new_user.add_analysis_dimension('user_id')
[outvalue_new_user.add_analysis_dimension(item) for item in ONLY_PRODUCT_ANALYSIS_DIMENSIONS]
#将分析转化成新集合
outvalue_new_user_session = outvalue_new_user.new_tableset_from_analysis_sql(as_name= 'table1')

outvalue_new_user_session.add_core_dimension('user_id', 'user_id', '用户ID')
outvalue_new_user_session.add_core_dimension('product_id', 'product_id', '产品ID')
outvalue_new_user_session.add_core_dimension('session_time', 'session_time', '全部玩家总游戏次数')

# 去掉内部group by
outvalue_new_user_session.deduplicate_on_core_dimensions=False
outvalue_new_user_session.add_core_filter('session_time', 'gt','10')

outvalue_register_user = outvalue_new_user_session.intersection(NEW_USER, on=['product_id',
                                                                                    'user_id'])
outvalue_register_user.add_analysis_metric('onu', 'user_id', '有效新增用户', 'COUNT_DISTINCT')
# 去掉内部group by
outvalue_register_user.deduplicate_on_core_dimensions=False
outvalue_register_user.add_analysis_output_const('ds', '{computation_ds}')
[outvalue_register_user.add_analysis_dimension(item) for item in ONLY_PRODUCT_ANALYSIS_DIMENSIONS]
[outvalue_register_user.add_analysis_grouping_set(item) for item in ONLY_PRODUCT_GROUPING_SETS]

ALL_ANALYSIS.append(outvalue_register_user)
# print (outvalue_register_user.analysis_sql())



# 日角色付费额
PAY_ROLE_DAILY = TableSet(source_table='matrix_domain')
PAY_ROLE_DAILY.add_core_dimension('product_id', 'get_json_object(data, \'$.matrix_sdk_context.matrix_token\')',
                                     '产品ID')
PAY_ROLE_DAILY.add_core_dimension('channel_id', 'get_json_object(data, \'$.context.channel_id\')', '渠道ID')
PAY_ROLE_DAILY.add_core_dimension('server_id', 'get_json_object(data, \'$.context.server_id\')', '服务器ID')
PAY_ROLE_DAILY.add_core_dimension('amount', 
                                  'COALESCE(get_json_object(data,\'$.context.amount\'),get_json_object(data,\'$.context.amount:\') ,\'0\')',
                                  '支付钱数')
PAY_ROLE_DAILY.add_core_dimension('ds', 'to_date(get_json_object(data, \'$.context.fixed_time_in_server_tz\'))', '支付时间')
PAY_ROLE_DAILY.add_core_dimension('part', 'part', '分区时间')
PAY_ROLE_DAILY.add_core_dimension('role_id', 'get_json_object(data, \'$.context.role_id\')', '角色ID')
PAY_ROLE_DAILY.add_core_dimension('event', 'get_json_object(data, \'$.event\')', '事件名')
PAY_ROLE_DAILY.add_core_dimension('domain', 'domain', '数据领域')
PAY_ROLE_DAILY.add_core_filter('domain', 'equal', 'user_rawdata')
PAY_ROLE_DAILY.add_core_filter('ds', 'equal', '{computation_ds}')
PAY_ROLE_DAILY.add_core_filter('part', 'equal', '{computation_ds}')
PAY_ROLE_DAILY.add_core_filter('event', 'equal', 'user pay')


daily_role_pay_money_analysis = PAY_ROLE_DAILY.copy()
# 去掉内部group by
daily_role_pay_money_analysis.deduplicate_on_core_dimensions=False

daily_role_pay_money_analysis.add_analysis_metric('drpm', 'amount/100', '日付费额', 'SUM')

daily_role_pay_money_analysis.add_analysis_output_const('ds', '{computation_ds}')
[daily_role_pay_money_analysis.add_analysis_dimension(item) for item in DEFAULT_ANALYSIS_DIMENSIONS]
[daily_role_pay_money_analysis.add_analysis_grouping_set(item)  for item in DEFAULT_GROUPING_SETS]

ALL_ANALYSIS.append(daily_role_pay_money_analysis)
# print (daily_role_pay_money_analysis.analysis_sql())



# ACU:平均同时在线玩家人数
active_user = ACTIVE_USER_DAILY.copy()
active_user.add_core_dimension('active_hour', 'hour(split(get_json_object(data, \'$.context.fixed_time_in_server_tz\'),\'T\')[1])', '活跃时间')
active_user.add_core_dimension('active_minute', 'cast((minute(split(get_json_object(data, \'$.context.fixed_time_in_server_tz\'),\'T\')[1])/5) as decimal(18,0))', '活跃时间')

# 去掉内部group by
active_user.deduplicate_on_core_dimensions=False

active_user.add_analysis_dimension('active_hour')
active_user.add_analysis_dimension('active_minute')
active_user.add_analysis_dimension('user_id')
active_user.add_analysis_dimension('product_id')


active_user_min = active_user.new_tableset_from_analysis_sql(as_name = 'T1')

active_user_min.add_core_dimension('product_id', 'product_id', '产品ID')
active_user_min.add_core_dimension('active_hour', 'active_hour', '活跃小时')
active_user_min.add_core_dimension('user_id', 'user_id', '用户ID')
active_user_min.add_core_dimension('value','active_minute','活跃分钟')
# 去掉内部group by
active_user_min.deduplicate_on_core_dimensions=False

active_user_hour = active_user_min.new_tableset_from_core_sql(as_name = 'T2')

active_user_hour.add_core_dimension('product_id', 'product_id', '产品ID')
active_user_hour.add_core_dimension('active_hour', 'active_hour', '活跃小时')
active_user_hour.add_core_dimension('user_id', 'user_id', '用户ID')
active_user_hour.add_core_dimension('value', 'value', '活跃分钟')

# 去掉内部group by
active_user_hour.deduplicate_on_core_dimensions=False

active_user_hour.add_analysis_metric('value', 'user_id', '每小时玩家数', 'COUNT_DISTINCT')
active_user_hour.add_analysis_dimension('active_hour')
[active_user_hour.add_analysis_dimension(item) for item in ONLY_PRODUCT_ANALYSIS_DIMENSIONS]

acerage_concurrent_user = active_user_hour.new_tableset_from_analysis_sql(as_name = 'T4')

acerage_concurrent_user.add_core_dimension('product_id', 'product_id', '产品ID')
acerage_concurrent_user.add_core_dimension('value', 'value', '活跃分钟')

# 去掉内部group by
acerage_concurrent_user.deduplicate_on_core_dimensions=False
acerage_concurrent_user.add_analysis_metric('acu', 'value', '平均同时在线玩家人数','SUM' , hook=lambda x: '%.2f' % (x/288))

acerage_concurrent_user.add_analysis_output_const('ds', '{computation_ds}')
[acerage_concurrent_user.add_analysis_dimension(item) for item in ONLY_PRODUCT_ANALYSIS_DIMENSIONS]
[acerage_concurrent_user.add_analysis_grouping_set(item)  for item in ONLY_PRODUCT_GROUPING_SETS]

ALL_ANALYSIS.append(acerage_concurrent_user)
# print (acerage_concurrent_user.analysis_sql())



# PCU：最高同时在线玩家人数
active_user = ACTIVE_USER_DAILY.copy()
active_user.add_core_dimension('active_hour', 'hour(split(get_json_object(data, \'$.context.fixed_time_in_server_tz\'),\'T\')[1])', '活跃时间')
active_user.add_core_dimension('active_minute', 'cast((minute(split(get_json_object(data, \'$.context.fixed_time_in_server_tz\'),\'T\')[1])/5) as decimal(18,0))', '活跃时间')

# 去掉内部group by
active_user.deduplicate_on_core_dimensions=False

active_user.add_analysis_dimension('active_hour')
active_user.add_analysis_dimension('active_minute')
active_user.add_analysis_dimension('user_id')
active_user.add_analysis_dimension('product_id')


active_user_min = active_user.new_tableset_from_analysis_sql(as_name = 'T1')

active_user_min.add_core_dimension('product_id', 'product_id', '产品ID')
active_user_min.add_core_dimension('active_hour', 'active_hour', '活跃小时')
active_user_min.add_core_dimension('user_id', 'user_id', '用户ID')
active_user_min.add_core_dimension('value','active_minute','活跃分钟')
# 去掉内部group by
active_user_min.deduplicate_on_core_dimensions=False

active_user_hour = active_user_min.new_tableset_from_core_sql(as_name = 'T2')

active_user_hour.add_core_dimension('product_id', 'product_id', '产品ID')
active_user_hour.add_core_dimension('active_hour', 'active_hour', '活跃小时')
active_user_hour.add_core_dimension('user_id', 'user_id', '用户ID')
active_user_hour.add_core_dimension('value', 'value', '活跃分钟')

# 去掉内部group by
active_user_hour.deduplicate_on_core_dimensions=False

active_user_hour.add_analysis_metric('value', 'user_id', '每小时玩家数', 'COUNT_DISTINCT')
active_user_hour.add_analysis_dimension('active_hour')
[active_user_hour.add_analysis_dimension(item) for item in ONLY_PRODUCT_ANALYSIS_DIMENSIONS]

peak_concurrent_users = active_user_hour.new_tableset_from_analysis_sql(as_name = 'T4')

peak_concurrent_users.add_core_dimension('product_id', 'product_id', '产品ID')
peak_concurrent_users.add_core_dimension('value', 'value', '活跃分钟')

# 去掉内部group by
peak_concurrent_users.deduplicate_on_core_dimensions=False
peak_concurrent_users.add_analysis_metric('pcu', 'value', '最高同时在线玩家人数','MAX')

peak_concurrent_users.add_analysis_output_const('ds', '{computation_ds}')
[peak_concurrent_users.add_analysis_dimension(item) for item in ONLY_PRODUCT_ANALYSIS_DIMENSIONS]
[peak_concurrent_users.add_analysis_grouping_set(item)  for item in ONLY_PRODUCT_GROUPING_SETS]

ALL_ANALYSIS.append(peak_concurrent_users)
# print (peak_concurrent_users.analysis_sql())



if __name__ == '__main__':
    
    print(total_pay_user.analysis_sql())

