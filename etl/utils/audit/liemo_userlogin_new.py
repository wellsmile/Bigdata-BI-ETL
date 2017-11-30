#coding=utf-8
'''
Created on 2017年2月20日

@author: xiaochengcao
'''

import arrow
import json
import sys

output_format = '%s\t%s\n'

userroledict = {}

with open('/mnt/disk1/tmp/caoxiaocheng/audit/liemotmp/gameuser.log','r') as userrolefile:
    
    for line in userrolefile:
        
        if line:
            userid = line.split('\t')[0]
            roleids = line.split('\t')[16]
            createdate = line.split('\t')[10]
            
            userroledict[userid] = '\t'.join([roleids,createdate])
        

with open('/mnt/disk1/tmp/caoxiaocheng/audit/liemotmp/userlogin.log','r') as loginlogfile:
    
    for loginlog in loginlogfile:
        
        if loginlog:
            event = 'user login'
            context = {}
            matrix_sdk_context = {}
            data_formatted = {}
            
            createdtime = loginlog.split('\t')[7]
            userid = loginlog.split('\t')[6]
            ip = loginlog.split('\t')[9]
            mobiletype = loginlog.split('\t')[2]
            
            server_time_str = createdtime + '+0800'
            server_time_str = str(arrow.get(server_time_str).for_json())
            
            context['channel_id'] = '-'
            context['fixed_time'] = server_time_str
            context['user_id'] = userid
            context['ip'] = ip
            context['mac'] = '-'
            context['device_type'] = mobiletype
            context['imei'] = '-'
            
            if userroledict.has_key(userid):
                roleids_createtime = userroledict[userid].split('\t')
                context['roleids'] = roleids_createtime[0]
                context['register_date'] = roleids_createtime[1]
            else:
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
