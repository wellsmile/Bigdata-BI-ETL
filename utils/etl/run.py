#coding=utf-8
'''
Created on 2017年5月9日

@author: xiaochengcao
'''
import datetime
import os
import time

start_date = datetime.date(2016,12,27)
end_date = datetime.date(2017,5,8)

while start_date <= end_date:
    start_time = time.time()
    start_date_str = str(start_date)
    print('\033[1;32;40m----------------------runing:'+start_date_str)
    command = 'python3 /opt/www/matrix-pixel/matrix-pixel/utils/etl/engine.py -y --update --date={0} --bothversion'.format(start_date_str)
    print(command + '\033[0m')
    os.system(command)
    start_date = start_date + datetime.timedelta(days = 1)
    print('\033[1;33;40m--'+start_date_str+'--success: '+str(int(time.time()-start_time))+' seconds\n\033[0m')
