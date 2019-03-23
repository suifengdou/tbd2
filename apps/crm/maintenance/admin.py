from django.contrib import admin

# Register your models here.

from .models import MaintenanceInfo, MaintenanceHandlingInfo, MaintenanceSummary

class MaintenanceInfoAdmin(admin.ModelAdmin):
    pass


class MaintenanceHandlingInfoAdmin(admin.ModelAdmin):
    pass


class MaintenanceSummaryAdmin(admin.ModelAdmin):
    pass


admin.site.register(MaintenanceInfo, MaintenanceInfoAdmin)
admin.site.register(MaintenanceHandlingInfo, MaintenanceHandlingInfoAdmin)
admin.site.register(MaintenanceSummary, MaintenanceSummaryAdmin)