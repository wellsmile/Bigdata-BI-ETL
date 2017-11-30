#coding=utf-8
'''
Created on Feb 10, 2017

@author: xiaochengcao
'''
import arrow
import MySQLdb
import json
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

if __name__ == '__main__':
    
    output_format = '%s\t%s\n'
    
    userimeidict = {}
    roleidsconn=MySQLdb.Connect(host='5860829caf7e0.bj.cdb.myqcloud.com',port=11247,user='cdb_outerroot',passwd='vO35F52vO35C6t8Q',db='bosdata',charset='utf8')
    roleidscursor = roleidsconn.cursor()
    roleidscursor.execute('select UID,CreateDate,DeviceID from gameuser')
    roleidsresult = roleidscursor.fetchall()
    
    for roleids in roleidsresult:
        createdate_str = str(roleids[1]) + '+0800'
        createdate_str = str(arrow.get(createdate_str).for_json())
        
        if roleids[2]:
            userimei = roleids[2]
        else:
            userimei = '-'
            
        if not userimeidict.has_key(str(roleids[0])):
            userimeidict[str(roleids[0])] = createdate_str + '\t' + userimei
    
    roleidsconn.close()
    
    tablelist = ['log_201608userloginlog','log_201609userloginlog','log_201610userloginlog','log_201611userloginlog','log_201612userloginlog']
    for tablename in tablelist:
        
        conn=MySQLdb.Connect(host='5860829caf7e0.bj.cdb.myqcloud.com',port=11247,user='cdb_outerroot',passwd='vO35F52vO35C6t8Q',db='boslog',charset='utf8')
        ordercursor = conn.cursor()
        ordercursor.execute('select AddTime,UID,Ip,MobileType from ' + tablename)
        orderresult=ordercursor.fetchall()
        
        conn.close()
        
        for sqlresult in orderresult:
        
            event = 'user login'
            context = {}
            matrix_sdk_context = {}
            data_formatted = {}
            
            createdtime = str(sqlresult[0])
            userid = sqlresult[1]
            ip = sqlresult[2]
            mobiletype = sqlresult[3]
            
            server_time_str = createdtime + '+0800'
            server_time_str = str(arrow.get(server_time_str).for_json())
            
            context['channel_id'] = '-'
            context['fixed_time'] = server_time_str
            context['user_id'] = userid
            context['ip'] = ip
            context['mac'] = '-'
            context['device_type'] = mobiletype
            
            if userimeidict.has_key(str(userid)):
                roleids_createtime_imei = userimeidict[str(userid)].split('\t')
                register_date = roleids_createtime_imei[0]
                context['imei'] = roleids_createtime_imei[1]
                try:
                    context['register_date'] = str(arrow.get(register_date).for_json())
                except Exception as e:
                    context['register_date'] = register_date
            else:
                context['imei'] = '-'
                context['roleids'] = '-'
                context['register_date'] = '-'
            
             
            matrix_sdk_context['matrix_sdk_api_version'] = '1.0.0'
            matrix_sdk_context['matrix_sdk_lang'] = 'java'
            matrix_sdk_context['matrix_sdk_platform'] = 'common'
            matrix_sdk_context['matrix_sdk_version'] = '1.0.0'
            matrix_sdk_context['matrix_token'] = '-'
             
            data_formatted['event'] = event
            data_formatted['context'] = context
            data_formatted['matrix_sdk_context'] = matrix_sdk_context
            
            json_data = json.dumps(data_formatted, ensure_ascii=False)
            
            output = output_format % (server_time_str, json_data)
            sys.stdout.write(output)
    
    
    
    
    
    