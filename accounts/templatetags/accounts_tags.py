#coding=utf-8
'''
Created on Feb 8, 2017

@author: Felix
'''
from django import template
import hashlib

register = template.Library()

@register.filter(name='md5')
def md5_string(value):
    return hashlib.md5(value.encode('utf-8')).hexdigest()