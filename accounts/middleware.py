#coding=utf-8
'''
Created on Dec 2, 2016

@author: Felix
'''
from django.conf import settings
from django.shortcuts import redirect

class CaptchaMiddleware(object):
    '''在session中保存请求的相关元数据，后续的展示逻辑可能会用到这些数据'''
    
    CHECK_PATH_LIST = ['/accounts/login/', 
                       '/accounts/signup/',
                       '/accounts/lock/'
                       ]
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        path = request.path
        _pre_response_flag = _post_response_flag = False
        
        if path in CaptchaMiddleware.CHECK_PATH_LIST:
            key = '{}_ACCESSTIMES'.format(path)
            value = request.session.get(key, 0) + 1
            request.session[key] = value # path access times in this session
            if value > settings.FORM_CAPTCHA_EDGE:
                _pre_response_flag = True
                request.session['_captcha'] = _pre_response_flag
            
        response = self.get_response(request)
        
        _post_response_flag = request.session.get('_captcha', False)
        
        if _pre_response_flag and not _post_response_flag: # user successfully did something, just reset the counter to zero
            for path in CaptchaMiddleware.CHECK_PATH_LIST:
                key = '{}_ACCESSTIMES'.format(path)
                request.session[key] = 0
        
        return response
        