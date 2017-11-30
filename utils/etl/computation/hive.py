#coding=utf-8
'''
Created on Jan 10, 2017

@author: Felix
'''
import logging
import json
import shlex
import subprocess
import sys

from .base import ComputeEngine

class Hive(ComputeEngine):
    def __init__(self, setting):
        super(Hive, self).__init__(setting)
        self.__init_engine()
    
    def __init_engine(self):
        conf = self._setting.conf
        conf = json.loads(conf)
        self._hive_host = conf.get('hive_host')
        self._hive_port = conf.get('hive_port')
        self._hive_dbname = conf.get('hive_dbname')
    
    def client(self):
        client = 'jdbc:hive2://{!s}:{!s}/{!s}'.format(self._hive_host, 
                                                      self._hive_port,
                                                      self._hive_dbname)
        return client
        
    def execute(self, **kwargs):
        client = self.client()
        cmd_tempalte = 'beeline -u {!s} -n hive --outputformat=tsv2 --showHeader=false -e {!r}'
        sql = kwargs.get('sql')
        timeout = kwargs.get('timeout', 86400)
        
        cmd_rendered = cmd_tempalte.format(client, sql)
        logging.debug('executing cmd {!r}'.format(cmd_rendered))
        
        try:
            args = shlex.split(cmd_rendered)
            complted_process = subprocess.run(args, 
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE,
                           timeout=timeout)
            
            if complted_process.returncode == 0:
                returned_data = complted_process.stdout.decode('utf-8').strip().split('\n')
                return returned_data
            else:
                print('HIVE ERROR: '+cmd_rendered)
                raise RuntimeError(complted_process.stderr)
        except Exception as e:
            print('HIVE ERROR: '+cmd_rendered)
            logging.exception(e)
            
if __name__ == '__main__':
    class Setting(object):
        def __init__(self):
            pass
    setting = Setting()
    setting.conf  = json.dumps({
        'hive_host':'localhost',
        'hive_port':'10000', 
        'hive_dbname':'matrix'
    })
    hiveobj = Hive(setting)
    resultlist = hiveobj.execute(sql='select * from matrix where part=20161106')
    sys.stdout.write(str(resultlist))