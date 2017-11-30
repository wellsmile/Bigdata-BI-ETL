#coding=utf-8
'''
Created on Jan 10, 2017

@author: Felix
'''
class ComputeEngine(object):
    def __init__(self, setting):
        self._setting = setting
    
    def __init_engine(self):
        raise NotImplementedError
    
    def execute(self, **kwargs):
        raise NotImplementedError