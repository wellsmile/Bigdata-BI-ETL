#coding=utf-8
'''
Created on 2017年2月17日

@author: xiaochengcao
'''

import datetime
import os

mysql_con = 'mysql -uselect -h106.75.15.149  -philink2017' # mysql连接信息
topic = 'gaoda_charge' # 查询主题，用于命名文件
now_date = datetime.date(2016,12,14) # 开始循环的时间
end_date = datetime.date(2017,1,1) # 结束时间的后一天
sql_command = 'select * from gaoda_czlog_s221.role_charge_card where date(optime) = \'{0}\' limit 5' # sql语句，不带分号，日期部分用 {0} 代替

first = True
while(now_date < end_date):
    print('----'+ topic + str(now_date) +'----')
    try:
        nowdatestr = str(now_date)
        sql_command_now = sql_command.format(nowdatestr)
        if first:
            addpartcommand = '{0} -e "{1}" >> {2}'.format(mysql_con, sql_command_now, topic)
        else:
            addpartcommand = '{0} -e "{1}" |tail -n1 >> {2}'.format(mysql_con, sql_command_now, topic)
        print(addpartcommand)
        os.system(addpartcommand)
        now_date = now_date + datetime.timedelta(days = 1)
        first = False
    except Exception as e:
        print(e)
    else:
        print('success')
