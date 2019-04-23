# -*- coding: utf-8 -*-
# @Time    : 2018/11/26 13:47
# @Author  : Hann
# @Site    : 
# @File    : urls.py
# @Software: PyCharm

from django.conf.urls import url

from .views import OrderList, MachineSNList, OrderUpload, ToMachineSN

urlpatterns = [
    url(r'^orderlist/$', OrderList.as_view(), name='orderlist'),
    url(r'^machinesn/$', MachineSNList.as_view(), name='machinesn'),
    url(r'^upload/$', OrderUpload.as_view(), name='upload'),
    url(r'^tomachinesn/$', ToMachineSN.as_view(), name='tomachinesn'),
    # url(r'^overview/$', MaintenanceOverview.as_view(), name='overview'),
    # url(r'^handlinglist/$', MaintenanceHandlinglist.as_view(), name='handlinglist'),
    # url(r'^signrepeat/$', MaintenanceSignRepeat.as_view(), name='signrepeat'),
    # url(r'^worklist/$', MaintenanceWorkList.as_view(), name='worklist'),



]