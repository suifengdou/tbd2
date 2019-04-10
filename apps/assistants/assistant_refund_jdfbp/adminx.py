# -*- coding: utf-8 -*-
# @Time    : 2019/4/10 9:03
# @Author  : Hann
# @Site    : 
# @File    : adminx.py.py
# @Software: PyCharm

import xadmin

from .models import RefundResource


class RefundResourceAdmin(object):
    list_display = ['service_order_id', 'order_id', 'goods_id', 'goods_name', 'order_status', 'application_time',
                    'buyer_expectation', 'return_model', 'handler_name', 'express_id', 'express_company']
    search_fields = ['service_order_id', 'order_id', 'express_id']
    list_filter = ['goods_id', 'application_time', 'order_status', 'return_model']


xadmin.site.register(RefundResource, RefundResourceAdmin)