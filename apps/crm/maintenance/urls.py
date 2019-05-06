# -*- coding: utf-8 -*-
# @Time    : 2018/11/26 13:47
# @Author  : Hann
# @Site    : 
# @File    : urls.py
# @Software: PyCharm

from django.conf.urls import url

from apps.crm.maintenance.views import MaintenanceList, MaintenanceOverview, MaintenanceUpload, MaintenanceHandlinglist, \
    MaintenanceToWork, MaintenanceSignRepeat, MaintenanceWorkList, MaintenanceToSN


urlpatterns = [
    url(r'^list/$', MaintenanceList.as_view(), name='list'),
    url(r'^overview/$', MaintenanceOverview.as_view(), name='overview'),
    url(r'^upload/$', MaintenanceUpload.as_view(), name='upload'),
    url(r'^handlinglist/$', MaintenanceHandlinglist.as_view(), name='handlinglist'),
    url(r'^towork/$', MaintenanceToWork.as_view(), name='towork'),
    url(r'^signrepeat/$', MaintenanceSignRepeat.as_view(), name='signrepeat'),
    url(r'^worklist/$', MaintenanceWorkList.as_view(), name='worklist'),
    url(r'^tomachinesn/$', MaintenanceToSN.as_view(), name='tomachinesn'),

]