from django.db import models
from django.utils.translation import ugettext_lazy as _

class Conception(models.Model):
    '''The conception abstraction'''
    name = models.CharField(verbose_name=_('Conception Name'), max_length=128)
    defination = models.TextField(verbose_name=_('Conception Defination'))
    date_added = models.DateTimeField(_('Date added'), auto_now_add=True)
    date_updated = models.DateTimeField(_('Date updated'), auto_now=True)
    
    def __str__(self):
        return self.name

class Dimension(models.Model):
    '''The Dimension abstraction'''
    name = models.CharField(verbose_name=_('Dimension Name'), max_length=128)
    event = models.CharField(verbose_name=_('Event Name'), max_length=128)
    defination = models.TextField(verbose_name=_('Dimension Defination'))
    date_added = models.DateTimeField(_('Date added'), auto_now_add=True)
    date_updated = models.DateTimeField(_('Date updated'), auto_now=True)
    
    def __str__(self):
        return self.name

