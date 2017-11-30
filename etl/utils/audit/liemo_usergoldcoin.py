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
    
    conn=MySQLdb.Connect(host='5860829caf7e0.bj.cdb.myqcloud.com',port=11247,user='cdb_outerroot',passwd='vO35F52vO35C6t8Q',db='boslog',charset='utf8')
    tablelist = ['log_201608usergoldcoinlog','log_201609usergoldcoinlog','log_201610usergoldcoinlog','log_201611usergoldcoinlog','log_201612usergoldcoinlog']
    for tablename in tablelist:
        ordercursor = conn.cursor()
        ordercursor.execute('select UID,OrIginType,CurrencyType,CostGold,CreateDateTime from ' + tablename)
        orderresult=ordercursor.fetchall()
        
        for sqlresult in orderresult:
        
            event = 'user goldchange'
            context = {}
            matrix_sdk_context = {}
            data_formatted = {}
            
            userid = sqlresult[0]
            costgold = sqlresult[3]
            createdtime = str(sqlresult[4])
            
            server_time_str = createdtime + '+0800'
            server_time_str = str(arrow.get(server_time_str).for_json())
            
            context['channel_id'] = '-'
            context['fixed_time'] = server_time_str
            context['user_id'] = userid
            
            context['role_id'] = '-'
            context['actiontype'] = 'dec'
            context['goldnum'] = costgold
            context['goldold'] = '-'
            context['goldnew'] = '-'
            
            context['rolename'] = '-'
            context['serverid'] = '-'
            context['lastloginip'] = '-'
             
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
    
    conn.close()
    
    
    
    
    