#coding=utf-8
'''
Created on Dec 1, 2016

@author: Felix
'''

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, {'template': 'index.html'},  name='index'),
    url(r'^report/$', views.report, {},  name='index'),
    url(r'^dashboard/$', views.dashboard, {'template': 'reports/dashboard.html'},  name='dashboard'),
    url(r'^retention_register/$', views.retention, {'template': 'reports/retention_register.html'},  name='retention_register'),
    url(r'^retention_active/$', views.retention, {'template': 'reports/retention_active.html'},  name='retention_active'),
    url(r'^retention_payment/$', views.retention, {'template': 'reports/retention_payment.html'},  name='retention_payment'),
    url(r'^revenue_dpm/$', views.revenue, {'template': 'reports/revenue_dpm.html'},  name='revenue_dpm'),
    url(r'^revenue_dpu/$', views.revenue, {'template': 'reports/revenue_dpu.html'},  name='revenue_dpu'),
    url(r'^revenue_dpr/$', views.revenue, {'template': 'reports/revenue_dpr.html'},  name='revenue_dpr'),
    url(r'^revenue_drpm/$', views.revenue, {'template': 'reports/revenue_drpm.html'},  name='revenue_drpm'),
    url(r'^revenue_dnp/$', views.revenue, {'template': 'reports/revenue_dnp.html'},  name='revenue_dnp'),
    url(r'^revenue_dnpm/$', views.revenue, {'template': 'reports/revenue_dnpm.html'},  name='revenue_dnpm'),
    url(r'^active_day/$', views.active, {'template': 'reports/active_day.html'},  name='active_day'),
    url(r'^active_week/$', views.active, {'template': 'reports/active_week.html'},  name='active_week'),
    url(r'^active_month/$', views.active, {'template': 'reports/active_month.html'},  name='active_month'),
    url(r'^meta/$', views.meta,  name='meta'),
    url(r'^search/$', views.get_doc_by_conditions,  name='search'),
]