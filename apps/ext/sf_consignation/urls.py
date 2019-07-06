# -*- coding: utf-8 -*-
# @Time    : 2018/11/26 13:47
# @Author  : Hann
# @Site    : 
# @File    : urls.py
# @Software: PyCharm

from django.conf.urls import url

from apps.ext.sf_consignation.views import ConsignationList, OperateOrder, ConsignationUpLoad, ConsignationOverView

urlpatterns = [
    url(r'^list/$', ConsignationList.as_view(), name='list'),
    url(r'^operate/$', OperateOrder.as_view(), name='operate'),
    url(r'^overview/$', ConsignationOverView.as_view(), name='overview'),
    url(r'^upload/$', ConsignationUpLoad.as_view(), name='upload'),


]