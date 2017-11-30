#coding=utf-8
'''
Created on 2017年2月13日

@author: xiaochengcao
'''
#coding=utf-8

import arrow
import json
import sys
from itertools import chain

reload(sys)
sys.setdefaultencoding('utf-8')

from collections import defaultdict
import geoip2.database

class IPManager(object):
    IPReader = geoip2.database.Reader('GeoLite2-City.mmdb')
    
    @classmethod
    def parse(cls, ip):
        try:
            response = cls.IPReader.city(ip)
            country_name = response.country.names['zh-CN'].encode('utf-8')
            province_name = response.subdivisions[0].names['zh-CN'].encode('utf-8') if response.subdivisions else '-'
            city_name = response.city.names['zh-CN'].encode('utf-8') if response.city.names else '-'
        except:
            country_name, province_name, city_name = ['-' for item in range(3)]
        
        return country_name, province_name, city_name


class ETLComputation(object):
    '''
    1. 计算session；
    2. 搜集用户ip地址；
    3. 补充缺少ip地址的事件；
    '''
    
    LINE_NO = 0
    def __init__(self, session_gap=600):
        self.inited = False # 本对象是否已经经过初始化
        
        # 公共信息
        self.matrix_token = None # 会话所在的产品ID
        self.user_id = None # 会话所对应的用户ID
        
        # session相关的变量
        self.session_gap = session_gap # 超过多少秒之后，算是一个会话的结束
        self.current_timestamp = None # 初始化时未收到任何数据，为None
        self.session_start = None
        self.session_end = None
        self.session_seconds = 0
        
        self.read_buffer = None # 公共缓冲区
        self.write_buffer = None # 公共缓冲区
        
        # 搜集用户IP信息所需要的变量
        self.ipinfo = defaultdict(lambda: defaultdict(int)) # 存储本用户对应的IP地址信息
        self.current_context_info = {'ip': None, 
                                     'role_id': None, 
                                     'server_id': None
                                     }
        
        # 用户界定不同的group之间的边界
        self.current_edge = None
    
    def init(self, matrix_token, user_id, fixed_time_str, data_str):
        self.edge_changed(matrix_token, user_id, fixed_time_str, data_str) #首次执行的时候，全新的开始，边界从无到有，算作一次变更
        self.init_session(matrix_token, user_id, fixed_time_str, data_str)
        self.init_buffer(matrix_token, user_id, fixed_time_str, data_str)
        self.inited = True # 标记为已经完成全部初始化工作
    
    def edge_changed(self, matrix_token, user_id, fixed_time_str, data_str):
        '''更新当前边界信息, 会在边界信息变更时被调用'''
        self.matrix_token = matrix_token # 重置应用标记
        self.user_id = user_id # 重置用户ID
        self.current_edge = '\t'.join([matrix_token, user_id])
        
        self.current_context_info['ip'] = None # 边际变更之后，当前处理组中的当前ip需要初始化为None，防止ip添加到下一个用户中的事件记录中
        self.ipinfo.clear() # 上一个用户的所有记录处理完成之后，需要重新初始化
        
    def init_buffer(self, matrix_token, user_id, fixed_time_str, data_str):
        '''清空事件缓冲区：比如一些待补充的信息的事件'''
        self.read_buffer = []
        self.write_buffer = []
    
    def init_session(self, matrix_token, user_id, fixed_time_str, data_str):
        fixed_time_obj = arrow.get(fixed_time_str)
        
        self.session_start = self.session_end = fixed_time_str
        self.session_seconds = 0 # 会话时间初始化为0
        self.current_timestamp = fixed_time_obj.timestamp # 保存新一组数据的第一个时间戳（外层已经按照时间排序）
    
    def input(self, line):
        keys = self.current_context_info.keys() # 待补充的键名称
        
        line = line.strip()
        matrix_token, user_id, fixed_time_str, data_str = line.split('\t')
        data_obj = json.loads(data_str)
        
        fixed_time_obj = arrow.get(fixed_time_str)
        fixed_time_timestamp = fixed_time_obj.timestamp
        
        platform = data_obj.get('matrix_sdk_context', {}).get('matrix_sdk_platform', None)
        
        edge = '\t'.join([matrix_token, user_id]) # 计算一个游戏内的，用户的会话划分边界
        
        if not self.inited: # 如果是刚开始执行，需要首先初始化
            self.init(matrix_token, user_id, fixed_time_str, data_str)
        
        if edge != self.current_edge: # 如果当前已经开启了新的group，就要输出所有需要输出的数据，并重新初始化
            self.end() # 先输出当前的各项数据，下面再进行下个组的初始化
            self.edge_changed(matrix_token, user_id, fixed_time_str, data_str)
        
        ### session computation
        timestamp_delta = fixed_time_timestamp - self.current_timestamp #  计算此条日志的时间戳同当前对象中持有的时间戳的差值
        timestamp_delta = abs(timestamp_delta) #  稳妥起见，取绝对值
        
        if timestamp_delta > self.session_gap:
            self.output_session() # reduce session输出
            self.init_session(matrix_token, user_id, fixed_time_str, data_str) # 只重新初始化session相关成员变量
        else:
            self.session_end = fixed_time_str
            self.session_seconds += timestamp_delta
            self.current_timestamp = fixed_time_timestamp
        ### session computation end
        
        ### ip gathering
        need_buffer = False # 是否需要缓存本条数据
        user_ip = None
        if platform == 'common': # 后端报送
            user_ip = data_obj.get('context', {}).get('ip', None) # 如果报送位置没有错误，则从正常的上下文中获取
            if user_ip in ('-', ''):
                user_ip = None
            
            if not user_ip:
                need_buffer = True
            
            user_ip = user_ip or data_obj.get('ip', None) # 后端报送位置错误的情况下
            
            matrix_ip = data_obj.get('matrix_sdk_context', {}).get('ip', None)
            if user_ip:
                self.ipinfo['backend_user'][user_ip] += 1
            if matrix_ip:
                self.ipinfo['backend_matrix'][matrix_ip] += 1
        else: # 前端报送
            matrix_ip = data_obj.get('matrix_sdk_context', {}).get('ip', None) # 前端报送的日志，在收集服务器收集到用户客户端IP地址就是用户的IP
            if matrix_ip:
                user_ip = matrix_ip
                self.ipinfo['frontend_matrix'][matrix_ip] += 1
            if user_ip:
                self.ipinfo['frontend_user'][user_ip] += 1
        ### ip gathering end
        
        data_context = data_obj.get('context')
        if user_ip: # 如果获取到用户的IP地址，设置当前IP地址
            self.current_context_info['ip'] = user_ip
        
        role_id = data_context.get('role_id', None)
        server_id = data_context.get('server_id', None)
        if role_id in ( '-', ''):
            role_id = None
            need_buffer = True
        if server_id in ('-', ''):
            server_id = None
            need_buffer = True
        
        if need_buffer: # 如果当前数据需要缓存，将其放入读缓存
            self.read_buffer.append(data_str)
        else:
            self.write_buffer.append(data_str)
        
        if role_id:
            self.current_context_info['role_id'] = role_id
        if server_id:
            self.current_context_info['server_id'] = server_id
        
        _new_read_buffer = []
        for _data_str in self.read_buffer:
            _data_obj = json.loads(_data_str)
            _data_context = _data_obj.get('context', {})
            _d = {} # 用来存储当前读缓存中，本条数据的待补充项及其值
            for _key in keys:
                _d[_key] = _data_context.get(_key, None)
            
            for _key in keys:
                if _d[_key] in (None, '-', ''):
                    _value = self.current_context_info.get(_key, None)
                    if _value:
                        _d[_key] = _value
                        _data_context[_key] = _value
            
            _data_obj['context'] = _data_context
            
            if all(_d.values()):
                self.write_buffer.append(json.dumps(_data_obj, ensure_ascii=False))
            else:
                _new_read_buffer.append(json.dumps(_data_obj, ensure_ascii=False))
        
        self.read_buffer = _new_read_buffer
        
        self.flush_buffer()
    
    def output_rawdata(self, data_str):
        ETLComputation.LINE_NO += 1
        rawdata_template = 'user_rawdata\t%s\n'
        sys.stdout.write(rawdata_template % data_str)
    
    def output_session(self):
        '''输出计算出的会话数据'''
        output = {
            'matrix_token': self.matrix_token,
            'user_id': self.user_id,
            'session_seconds': self.session_seconds,
            'session_start': self.session_start,
            'session_end': self.session_end
        }
        output_str = json.dumps(output, ensure_ascii=False)
        output_str = '\t'.join(['user_sessions', output_str]) + '\n'
        sys.stdout.write(output_str)
    
    def output_region(self):
        user_ips = {}
        
        backend_user = self.ipinfo.get('backend_user', {})
        frontend_user = self.ipinfo.get('frontend_user', {})
        
        for ip in backend_user:
            user_ips[ip] = backend_user[ip]
            if frontend_user.has_key(ip):
                user_ips[ip] += frontend_user.get(ip, 0)
                frontend_user.pop(ip)
        
        for ip in frontend_user:
            user_ips[ip] = frontend_user[ip]
        
        for user_ip in user_ips:
            country_name, province_name, city_name = IPManager.parse(user_ip)
            output_info = {
                'matrix_token': self.matrix_token,
                'user_id': self.user_id,
                'ip': user_ip,
                'occur_times': user_ips[user_ip],
                'country': country_name,
                'province': province_name,
                'city': city_name
            }
            _output_info = json.dumps(output_info, ensure_ascii=False)
            output_str = '\t'.join(['user_regions', _output_info]) + '\n'
            sys.stdout.write(output_str)
    
    def flush_buffer(self):
        sys.stderr.write('flushing: %s\n' % len(self.write_buffer))
        for _data_str in self.write_buffer: # 补充补IP的相关事件的缓存
            self.output_rawdata(_data_str) 
        self.write_buffer = []
    
    def flush_buffer_force(self):
        '''强制刷新缓存，并将缓存置空'''
        sys.stderr.write('force flushing: %s\n' % (len(self.write_buffer) + len(self.read_buffer)))
        for _data_str in chain(self.read_buffer, self.write_buffer):
            self.output_rawdata(_data_str)
        self.read_buffer, self.write_buffer = [], []
    
    def end(self):
        self.flush_buffer_force()  # 输出缓存数据
        self.output_session() # 输出会话数据
        self.output_region() # 输出地理位置数据
    
if __name__ == '__main__':
    etlComputation = ETLComputation(session_gap=600)
    
    for line in sys.stdin:
        line = line.strip()
        session_output_str = etlComputation.input(line)
        
        if ETLComputation.LINE_NO % 10000 == 0:
            sys.stderr.write('OUTPUTED RAW DATA : %s\n' % ETLComputation.LINE_NO)
    
    if etlComputation.inited:
        etlComputation.end()