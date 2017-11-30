#coding=utf-8
'''
Created on Feb 10, 2017

@author: Felix
'''
import arrow
import json
import sys

if __name__ == '__main__':
    output_format = '%s\t%s\n'
    for line in sys.stdin:
        try:
            data_formatted = {}
            
            data_str = line.strip()
            data = json.loads(data_str)
            
            timezone = '+0800'
            event = 'user login'
            server_time_str = data.get('loginTime', None)
            if server_time_str:
                if server_time_str.isdigit():
                    server_time_ts = int(server_time_str) # Java中单位是毫秒
                    server_time_ts = server_time_ts / 1000 # 转换成秒
                    server_time = arrow.get(server_time_ts).to(timezone)
                else:
                    server_time = arrow.get(server_time_str)
                    
                server_time = server_time.for_json()
                context = {}
                matrix_sdk_context = {}
            
                context['channel_id'] = data.get('channelID', '-')
                context['device_type'] = data.get('device_type' ,'-')
                context['fixed_time'] = server_time
                context['imei'] = data.get('IMEI', '-')
                context['mac'] = data.get('MAC', '-')
                context['user_id'] = data.get('userID', '-')
                
                matrix_sdk_context['ip'] = data.get('userIP', '-')
                matrix_sdk_context['matrix_sdk_api_version'] = '1.0.0'
                matrix_sdk_context['matrix_sdk_lang'] = 'java'
                matrix_sdk_context['matrix_sdk_platform'] = 'common'
                matrix_sdk_context['matrix_sdk_version'] = '1.0.0'
                matrix_sdk_context['matrix_token'] = data.get('appID')
                
                data_formatted['event'] = event
                data_formatted['context'] = context
                data_formatted['matrix_sdk_context'] = matrix_sdk_context
                
                json_data = json.dumps(data_formatted, ensure_ascii=False)
                output = output_format % (server_time, json_data)
                sys.stdout.write(output)
        except:
            pass
        