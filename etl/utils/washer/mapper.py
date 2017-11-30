#coding=utf-8
'''
Created on Feb 9, 2017

@author: Felix
'''

import json
import sys
import arrow

reload(sys)
sys.setdefaultencoding('utf-8')

EXCLUDE_TOKENS = ['22e6edc2448d4a889534a7d4f433a4cf', 
                  '4fbff88cb11e43bfbb4ef598032420b3']

def cleaner_time(server_time_str, data_str, deltaseconds=86400):
    '''根据服务器收到日志的时间，修正差距较大的日志的时间'''
    # 提取相关数据
    reason = ''
    server_time = arrow.get(server_time_str)
    server_time_tz = server_time.format('Z') # 数据收集服务器时区
    
    data = json.loads(data_str)
    data_context = data.get('context', {}) # 引用传递
    matrix_context = data.get('matrix_sdk_context', {})
    if data_context:
        # 修正本条数据的时间
        fixed_time_str = data_context.get('fixed_time', None)
        if fixed_time_str:
            fixed_time = arrow.get(fixed_time_str)
            fixed_time_tz = fixed_time.format('Z') # 发送数据中的时区信息
              
            if fixed_time_str.isdigit(): 
                fixed_time_tz = server_time_tz # 如果是时间戳格式，则报送中缺少了时区信息，默认使用服务器的时区信息
                reason += 'use server tz;'
            # 计算服务器时间与数据的报送的时间的差距（以秒为单位）
            delta = server_time.timestamp - fixed_time.timestamp
            delta = abs(delta)
            if delta > deltaseconds:
                fixed_time = arrow.get(server_time.timestamp).to(fixed_time_tz)
                reason += 'use server ts;'
                data_context['fixed_time'] = fixed_time.for_json()
                data_context['mod_reason'] = reason
            
            # 统一标记一下服务器时区格式，便于后续计算
            fixed_time_in_server_tz = fixed_time.to(server_time_tz)
            # 将报送时间中的时区和转换成服务器时区的时间都附加到数据中
            data_context['fixed_time_tz'] = fixed_time_tz # 看作是用户真实的时区信息
            data_context['fixed_time_in_server_tz'] = fixed_time_in_server_tz.for_json() # 将时间表示统一到服务器时间时区上
            
    data_str = json.dumps(data)
    return data_str

if __name__ == '__main__':
    skipped_lines = 0
    for line in sys.stdin:
        line = line.strip()
        server_time_str, data_str = line.split('\t')
        
        try:
            data_str = cleaner_time(server_time_str, data_str) # 修复时间
        except ValueError as e:
            skipped_lines += 1
        try:
            data = json.loads(data_str, encoding='utf-8')
            data_context = data.get('context', {})
            data_matrix_sdk_context = data.get('matrix_sdk_context', {})
            
            matrix_token = data_matrix_sdk_context.get('matrix_token', None)
            if matrix_token in EXCLUDE_TOKENS:
                skipped_lines += 1
                continue
            
            user_id = data_context.get('user_id', '-')
            matrix_token = data_matrix_sdk_context.get('matrix_token', '-')
            fixed_time_in_server_tz = data_context.get('fixed_time_in_server_tz', None)
            
            if not fixed_time_in_server_tz:
                skipped_lines += 1
                sys.stderr.write('fixed_time_in_server_tz is None!\n')
                continue
            sys.stdout.write('%s\t%s\t%s\t%s\n' % (matrix_token, 
                                                   user_id,
                                                   fixed_time_in_server_tz,
                                                   data_str))
        except Exception, e:
            skipped_lines += 1
            sys.stderr.write('%s\t%s\n' % (skipped_lines, str(e)))
    sys.stderr.write('%s\n' % skipped_lines)
