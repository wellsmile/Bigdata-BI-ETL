from django.db import models

from django.utils.translation import ugettext_lazy as _

class ComputeEngine(models.Model):
    '''The compute engine'''
    
    COMPUTE_ENGINE_TYPE_CHOICE = (('HIVE', 'Hive'),
                                  ('PRESTO', 'Presto'))
    
    name = models.CharField(_('Name of the compute engine'), max_length=128)
    ctype = models.CharField(_('Compute Engine Type'), 
                                     choices=COMPUTE_ENGINE_TYPE_CHOICE,
                                     default=COMPUTE_ENGINE_TYPE_CHOICE[0][0],
                                     max_length=32)
    desc = models.TextField(_('Description of the engine'))
    conf = models.TextField(_('Configuration of the compute engine'))
    date_added = models.DateTimeField(_('Date added'), auto_now_add=True)
    date_updated = models.DateTimeField(_('Date updated'), auto_now=True)
    
    def __str__(self):
        return self.name

class StorageEnigne(models.Model):
    '''classified by usage: context or final result'''
    
    STORAGE_TYPE_CHOICE = (('CONTEXT', _('Context Storage')),
                           ('RESULT', _('Result Storage')),
                           )
    
    STORAGE_ENGINE_TYPE_CHOICE = (('ELASTICSEARCH', _('Elasticsearch')),
                                  ('REDIS', _('Redis')),
                                  ('MYSQL', _('MySQL')),
                                  )
    
    name = models.CharField(_('Name of the storage'), max_length=128)
    desc = models.TextField(_('Description of the storage'))
    stype = models.CharField(_('Storage type'), 
                                     choices=STORAGE_TYPE_CHOICE,
                                     default=STORAGE_TYPE_CHOICE[0][0],
                                     max_length=32)
    setype = models.CharField(_('Storage engine type'),
                                      choices=STORAGE_ENGINE_TYPE_CHOICE,
                                      default=STORAGE_ENGINE_TYPE_CHOICE[0][0],
                                      max_length=32)
    conf = models.TextField(_('Configuration of the storage'))
    date_added = models.DateTimeField(_('Date added'), auto_now_add=True)
    date_updated = models.DateTimeField(_('Date updated'), auto_now=True)
    
    def __str__(self):
        return self.name

class DatawarehouseComputeConfiguration(models.Model):
    '''Compute configuration for the whole data warehouse'''
    
    COMPUTE_LAYER_CHOICE = ((0, _('Base Conceptions Extraction Layer')),
                            (1, _('Flexible Dimension Extraction Layer')),
                            (2, _('Fixed Dimension Extraction Layer')),
                            (3, _('Data Aggregation Layer')))
    
    name = models.CharField(_('Name of the compute configuration'), max_length=128)
    desc = models.TextField(_('Description of the configuration'))
    engine = models.ForeignKey(ComputeEngine, verbose_name=_('Engine to be used'))
    layer = models.SmallIntegerField(_('The layer of the configuration'), 
                                     choices=COMPUTE_LAYER_CHOICE)
    template = models.TextField(_('Compute template'))
    output = models.TextField(_('The output configuration'), 
                              blank=True, 
                              null=True, 
                              default='')
    date_added = models.DateTimeField(_('Date added'), auto_now_add=True)
    date_updated = models.DateTimeField(_('Date updated'), auto_now=True)
    
    def __str__(self):
        return self.name
    
class ReportUnit(models.Model):
    '''Compute configuration for all the report units'''
    name = models.CharField(_('Name of the Report unit'), max_length=128)
    refer = models.CharField(_('Refer name of the report unit'), max_length=128)
    unitname = models.CharField(_('Unit name of the report unit'), max_length=128, default='ds')
    desc = models.TextField(_('Help text of the report'))
    engine = models.ForeignKey(ComputeEngine, verbose_name=_('Engine to be used'))
    template = models.TextField(_('Compute template'))
    output = models.TextField(_('The output configuration')) 
    dimension = models.TextField(_('The dimension configuration'), default='[]')
    visualization = models.TextField(_('The visualization configuration'))
    date_added = models.DateTimeField(_('Date added'), auto_now_add=True)
    date_updated = models.DateTimeField(_('Date updated'), auto_now=True)
    
    def __str__(self):
        return self.name
    
class ProductIdName(models.Model):
    '''match product_id and name'''
    product_id = models.CharField(_('Id of the product'), max_length=128)
    name = models.CharField(_('Name of the product'), max_length=128)
    
    def __str__(self):
        return self.name