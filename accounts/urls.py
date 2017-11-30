#coding=utf-8
'''
Created on Dec 1, 2016

@author: Felix
'''
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^captcha/$', views.captcha, name='captcha'),
    url(r'^login/$', views.login_, {'template': 'accounts/login.html'}),
    url(r'^logout/$', views.logout_, {}),
    url(r'^lock/$', views.lock, {'template': 'accounts/lock.html'}),
    url(r'^signup/$', views.signup, {'template': 'accounts/signup.html'}),
    url(r'^profile/$', views.profile, {'template': 'accounts/profile.html'}),
    url(r'^changepassword/$', views.changepassword, {'template': 'accounts/changepassword.html'}),
    url(r'^resetpassword/$', views.resetpassword, {'resetpassword1st_template': 'accounts/resetpassword1st.html', 
                                                   'resetpassword2nd_template': 'accounts/resetpassword2nd.html'}),
]