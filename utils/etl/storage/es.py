#coding=utf-8
'''
Created on Jan 10, 2017

@author: Felix
'''

from elasticsearch import Elasticsearch
import logging.handlers
import json

from .base import StorageEngine
from elasticsearch.exceptions import NotFoundError

class ES(StorageEngine):
    def __init__(self, setting):
        super(ES, self).__init__(setting)
        conf = self._setting.conf
        name = self._setting.name
        conf_dict = json.loads(conf)
        self._es_connect = conf_dict.get('connect_settings')
        self._es_index = conf_dict.get('index_name')
        self._es_doctype = conf_dict.get('type_name','')
        self.es = Elasticsearch(self._es_connect)
        self.es_logger = self.__init_logger__(name, '/data/log/elasticsearch/es_log.log')
        self.es_logger_format = '{connect_info}\t{event}\t{affect_data}\t{result}'
        
    def __init_logger__(self, name, local):
        '''init the logger object'''
        logger = logging.Logger(name)
        logger.setLevel('DEBUG')
        formatter = logging.Formatter('%(name)s\t%(asctime)s\t%(message)s', '%Y-%m-%d %H:%M:%S')
        self.rotate_file_handler = logging.handlers.RotatingFileHandler(local, maxBytes = 1073741824, mode = 'a', backupCount = 9999)
        self.rotate_file_handler.setFormatter(formatter)  
        logger.addHandler(self.rotate_file_handler)
        return logger
    
    def put(self, **kwargs):
        '''index doc'''
        doc = kwargs.get('doc', {})
        add_log = kwargs.get('add_log', True)
        only_log = kwargs.get('only_log', False)
        resultbool = False
        if not only_log:
            esput_resp = self.es.index(index=self._es_index, doc_type=self._es_doctype, body=doc)
            resultbool = esput_resp.get('created', False)
        if add_log:
            log_dict = {
                'connect_info': self._setting.conf,
                'event': 'PUT', 
                'affect_data': json.dumps(doc), 
                'result': str(resultbool)
                }
            self.es_logger.info(self.es_logger_format.format(**log_dict))
        return resultbool # return the bool value, put success or not
    
    def puts(self, **kwargs):
        '''index many docs'''
        docs = kwargs.get('docs', [])
        resultnum = 0
        for doc in docs:
            resultbool = self.put(doc = doc)
            if resultbool or resultbool=='True':
                resultnum += 1
        return resultnum # return the num of put docs
    
    def get(self, **kwargs):
        '''search docs by conditions'''
        if not self._es_doctype:
            self._es_doctype = 'all'
        conditions = kwargs.get('conditions', None) # conditions dict
        esget_resp = self.es.search(index=self._es_index, doc_type=self._es_doctype, body=conditions, size=9999)
        hitslist = esget_resp.get('hits').get('hits')
        resultlist = [ i.get('_source') for i in hitslist ]
        return resultlist # return the result list
    
    def delete(self, **kwargs):
        '''delete docs by conditions'''
        conditions = kwargs.get('conditions', None) # conditions dict
        add_log = kwargs.get('add_log', True)
        only_log = kwargs.get('only_log', False)
        try:
            resultnum = 0
            if not only_log:
                esdelete_resp = self.es.delete_by_query(index=self._es_index, doc_type=self._es_doctype, body=conditions, conflicts='proceed')
                resultnum = esdelete_resp.get('deleted', 0)
        except NotFoundError:
            resultnum = 0
        if add_log:
            log_dict = {
                'connect_info': self._setting.conf,
                'event': 'DELETE', 
                'affect_data': json.dumps(conditions), 
                'result': str(resultnum)
                }
            self.es_logger.info(self.es_logger_format.format(**log_dict))
        
        return resultnum # return the num of deleted

