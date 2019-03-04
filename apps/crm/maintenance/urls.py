# -*- coding: utf-8 -*-
# @Time    : 2018/11/26 13:47
# @Author  : Hann
# @Site    : 
# @File    : urls.py
# @Software: PyCharm

from django.conf.urls import url


from apps.crm.maintenance.views import MaintenanceList, MaintenanceOverview, MaintenanceUpload, MaintenanceHandlinglist


urlpatterns = [
    url(r'^list/$', MaintenanceList.as_view(), name='list'),
    # url(r'^operate/$', Main.as_view(), name='operate'),
    url(r'^overview/$', MaintenanceOverview.as_view(), name='overview'),
    url(r'^upload/$', MaintenanceUpload.as_view(), name='upload'),
    url(r'^handlinglist/$', MaintenanceHandlinglist.as_view(), name='handlinglist'),



]