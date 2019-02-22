# -*- coding: utf-8 -*-
# @Time    : 2018/11/26 13:47
# @Author  : Hann
# @Site    : 
# @File    : urls.py
# @Software: PyCharm

from django.conf.urls import url


from apps.crm.orders.views import OrderList, OrderToCustomer, OrderOverview, OrderUpload

urlpatterns = [
    url(r'^list/$', OrderList.as_view(), name='list'),

    url(r'^overview/$', OrderOverview.as_view(), name='overview'),
    url(r'^otc/$', OrderToCustomer.as_view(), name='otc'),
    url(r'^upload/$', OrderUpload.as_view(), name='upload'),

]