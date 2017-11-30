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
    
    conn=MySQLdb.Connect(host='5860829caf7e0.bj.cdb.myqcloud.com',port=11247,user='cdb_outerroot',passwd='vO35F52vO35C6t8Q',db='bosdata',charset='utf8')
    ordercursor = conn.cursor()
    ordercursor.execute('select money,channelID,currency,createdTime,orderID,UID,appID,IP from gameorder where state=3')
    orderresult=ordercursor.fetchall()
    
    for sqlresult in orderresult:
    
        event = 'user pay'
        context = {}
        matrix_sdk_context = {}
        data_formatted = {}
        
        money = sqlresult[0]
        channel_id = sqlresult[1]
        currency = sqlresult[2]
        createdtime = str(sqlresult[3])
        orderid = sqlresult[4]
        userid = sqlresult[5]
        appid = sqlresult[6]
        ip = sqlresult[7]
        
        server_time_str = createdtime + '+0800'
        server_time_str = str(arrow.get(server_time_str).for_json())
        
        context['amount'] = money
        context['channel_id'] = channel_id
        context['currency'] = currency
        context['fixed_time'] = server_time_str
        context['orderid'] = orderid
        context['user_id'] = userid
        context['status'] = 'success'
        context['ip'] = ip
        
        context['role_id'] = '-'
        context['role_name'] = '-'
        context['server_id'] = '-'
        context['server_name'] = '-'
        
         
        matrix_sdk_context['matrix_sdk_api_version'] = '1.0.0'
        matrix_sdk_context['matrix_sdk_lang'] = 'java'
        matrix_sdk_context['matrix_sdk_platform'] = 'common'
        matrix_sdk_context['matrix_sdk_version'] = '1.0.0'
        matrix_sdk_context['matrix_token'] = appid
         
        data_formatted['event'] = event
        data_formatted['context'] = context
        data_formatted['matrix_sdk_context'] = matrix_sdk_context
        
        json_data = json.dumps(data_formatted, ensure_ascii=False)
        
        output = output_format % (server_time_str, json_data)
        sys.stdout.write(output)
    
    conn.close()
    
    
    
    
    