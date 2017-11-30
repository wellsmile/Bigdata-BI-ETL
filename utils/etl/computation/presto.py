#coding=utf-8
'''
Created on Jan 10, 2017

@author: Felix
'''
from .base import ComputeEngine

class Presto(ComputeEngine):
    def __init__(self, setting):
        super(Presto, self).__init__(setting)
    
    def __init_engine(self):
        ComputeEngine.__init_engine(self)
    
    def execute(self, **kwargs):
        ComputeEngine.execute(self, **kwargs)