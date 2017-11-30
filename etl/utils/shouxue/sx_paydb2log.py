#coding=utf-8
'''
Created on Feb 10, 2017

@author: Felix
'''
import arrow
import json
import sys

lineno = 0
keys = None
output_format = '%s\t%s\n'
with open('pay_2016.log', encoding='utf-8') as paylog:
    for line in paylog:
        lineno += 1
        line = line.strip()
        if lineno == 1:
            keys = line.split('\t')
            continue
        
        values = line.split('\t')
        kv_pairs = zip(keys, values)
        kv_dict = dict(kv_pairs)
        
        data_formatted = {}
        
        server_time_str = kv_dict['createdTime'] + '+0800'
        server_time_str = arrow.get(server_time_str).for_json()
        
        event = 'user pay'
        context = {}
        matrix_sdk_context = {}
        
        context['amount'] = kv_dict.get('money', '-')
        context['channel_id'] = kv_dict.get('channelID', '-')
        context['currency'] = kv_dict.get('currency')
        context['fixed_time'] = server_time_str
        context['orderid'] = kv_dict.get('orderID', '-')
        context['role_id'] = kv_dict.get('roleID', '-')
        context['role_name'] = kv_dict.get('roleName', '-')
        context['server_id'] = kv_dict.get('serverID', '-')
        context['server_name'] = kv_dict.get('serverName', '-')
        context['user_id'] = kv_dict.get('userID', '-')
        context['status'] = 'success'
        
        matrix_sdk_context['matrix_sdk_api_version'] = '1.0.0'
        matrix_sdk_context['matrix_sdk_lang'] = 'java'
        matrix_sdk_context['matrix_sdk_platform'] = 'common'
        matrix_sdk_context['matrix_sdk_version'] = '1.0.0'
        matrix_sdk_context['matrix_token'] = kv_dict.get('appID', '-')
        
        data_formatted['event'] = event
        data_formatted['context'] = context
        data_formatted['matrix_sdk_context'] = matrix_sdk_context
        
        json_data = json.dumps(data_formatted, ensure_ascii=False)
        
        state = kv_dict.get('state')
        if state in ('2', '3'):
            output = output_format % (server_time_str, json_data)
            sys.stdout.write(output)