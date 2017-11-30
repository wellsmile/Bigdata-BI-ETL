from django.db import models
from django.utils.translation import ugettext_lazy as _

class App(models.Model):
    '''App Management'''
    token = models.CharField(verbose_name=_('APP ID'), max_length=128)
    name = models.CharField(verbose_name=_('APP name'), max_length=128)
    key = models.CharField(verbose_name=_('APP Key'), max_length=128)
    secret = models.CharField(verbose_name=_('APP Secret'), max_length=128)
    date_added = models.DateTimeField(_('Date added'), auto_now_add=True)
    date_updated = models.DateTimeField(_('Date updated'), auto_now=True)
    
    def __str__(self):
        return self.name

