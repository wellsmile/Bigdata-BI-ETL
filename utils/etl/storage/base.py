#coding=utf-8
'''
Created on Jan 10, 2017

@author: Felix
'''

class StorageEngine(object):
    def __init__(self, setting):
        self._setting = setting
    
    def put(self, **kwargs):
        raise NotImplementedError
    
    def get(self, **kwargs):
        raise NotImplementedError