#coding=utf-8
'''
Created on Feb 10, 2017

@author: xiaochengcao
'''
import json
import sys
import MySQLdb

reload(sys)
sys.setdefaultencoding('utf-8')

gamelist = ['foa','gaoda','dmxlda']

for game in gamelist:
    conn=MySQLdb.Connect(host='rm-2ze7f85494p1i7i7r.mysql.rds.aliyuncs.com',port=3306,user='heyijoy',passwd='heyi20!^#',db='audit_'+game,charset='utf8')
    cursor = conn.cursor()
    with open('/mnt/disk1/tmp/caoxiaocheng/unaudit/mrfiles/{0}/{1}.log'.format(game,game),'r') as gaodafile:
        for gaodaline in gaodafile:
            domain = gaodaline.split('\t')[0]
            datastr = gaodaline.split('\t')[1]
            if domain == 'user_rawdata':
                data_json = json.loads(datastr)
                event = data_json.get('event',None)
                logid = data_json.get('context',{}).get('log_id',None)
                ip = data_json.get('context',{}).get('ip',None)
                if event == 'user pay':
                    cursor.execute('update role_pay set ip="' + str(ip) + '" where log_id =' + str(logid) +';')
                    print(game +' user pay has fixed ip: '+str(ip)+' ,log_id: '+str(logid))
                elif event == 'user login':
                    imei = data_json.get('context',{}).get('imei',None)
                    cursor.execute('update role_login set ip="' + str(ip) + '" where log_id =' + str(logid) +';')
                    print(game +' user login has fixed ip: '+str(ip)+' ,log_id: '+str(logid))
                    cursor.execute('update role_login set imei="' + str(imei) + '" where log_id =' + str(logid) +';')
                    print(game +' user login has fixed imei: '+str(imei)+' ,log_id: '+str(logid))
            else:
                pass
    conn.commit()
    conn.close()