import json

from django.contrib import admin

from .models import ComputeEngine, \
                    StorageEnigne, \
                    DatawarehouseComputeConfiguration, \
                    ReportUnit, \
                    ProductIdName

class ReportUnitAdmin(admin.ModelAdmin):
    search_fields = ('name', 'desc')
    list_display = ('name', 'get_desc')
    ordering = ('name','name')
    
    def save_model(self, request, obj, form, change):
        dimensions = json.loads(obj.dimension)
        dimensions.sort()
        if not dimensions:
            dimensions = ['matrix_token']
        obj.unitname = '_'.join(dimensions)
        obj.save()
    
    def get_desc(self, obj):
        return '-----'.join(str(obj.desc).split('\n')[:2])
    get_desc.short_description = 'help descript'
    
    
admin.site.register(ComputeEngine)
admin.site.register(StorageEnigne)
admin.site.register(DatawarehouseComputeConfiguration)
admin.site.register(ReportUnit, ReportUnitAdmin)
admin.site.register(ProductIdName)
