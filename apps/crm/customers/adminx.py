# -*- coding: utf-8 -*-
# @Time    : 2020/11/21 10:58
# @Author  : Hann
# @Site    : 
# @File    : adminx.py
# @Software: PyCharm

import math, re
import datetime
import pandas as pd
import emoji
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.db import router
from django.utils.encoding import force_text
from django.template.response import TemplateResponse
from django.db.models import Sum, Avg, Min, Max, F

from django.contrib.admin.utils import get_deleted_objects

from django.core.files.uploadedfile import InMemoryUploadedFile

import xadmin
from xadmin.plugins.actions import BaseActionView
from xadmin.views.base import filter_hook
from xadmin.util import model_ngettext
from xadmin.layout import Fieldset, Main, Row, Side

from .models import CustomerInfo, CountIdList, OrderList


class CustomerInfoAdmin(object):
    list_display = ['mobile', 'e_mail', 'qq', 'wangwang', 'jdfbp_id', 'jdzy_id', 'gfsc_id', 'alipay_id', 'pdd_id',
                    'wechat', 'others_id', 'birthday', 'total_amount', 'total_times', 'last_time', 'return_time',
                    'contact_times', 'free_service_times', 'maintenance_times', 'memorandum', 'order_failure_times',
                    'creator', 'create_time']
    readonly_fields = ['mobile', 'e_mail', 'qq', 'wangwang', 'jdfbp_id', 'jdzy_id', 'gfsc_id', 'alipay_id', 'pdd_id',
                       'wechat', 'others_id', 'birthday', 'total_amount', 'total_times', 'last_time', 'return_time',
                       'contact_times', 'free_service_times', 'maintenance_times', 'memorandum', 'order_failure_times',
                       'creator', 'create_time', 'update_time', 'is_delete']

    list_filter = ['mobile', 'wangwang', 'jdfbp_id', 'jdzy_id', 'gfsc_id',]

    form_layout = [
        Fieldset('基本信息',
                 Row('mobile',),),
        Fieldset('ID信息',
                 Row('wangwang', 'jdfbp_id', 'jdzy_id', ),

                 Row('gfsc_id', 'alipay_id', 'pdd_id', ),
                 Row('wechat', 'others_id',),),
        Fieldset('计数信息',
                 Row('total_amount', 'total_times',),
                 Row('free_service_times', 'maintenance_times',),
                 Row('order_failure_times',),),
        Fieldset(None,
                 'creator', 'create_time', 'update_time', 'is_delete', **{"style": "display:None"}),
    ]

    batch_data = True
    mobile_ids = []

    def post(self, request, *args, **kwargs):
        ids = request.POST.get('ids', None)
        if ids is not None:
            if " " in ids:
                ids = ids.split(" ")
                self.mobile_ids = []
                self.mobile_ids = ids
                self.queryset()
            else:
                self.mobile_ids = []
                self.mobile_ids.append(str(ids).replace("/t", "").replace("/n", "").replace(" ", ""))
                self.queryset()

        return super(CustomerInfoAdmin, self).post(request, *args, **kwargs)

    def queryset(self):
        queryset = super(CustomerInfoAdmin, self).queryset()

        if self.mobile_ids:
            queryset = super(CustomerInfoAdmin, self).queryset().filter(is_delete=0, mobile__in=self.mobile_ids)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


class CountIdListAdmin(object):
    list_display = ['ori_order_trade_no']
    readonly_fields = ['ori_order_trade_no', 'creator', 'create_time', 'update_time', 'is_delete']
    list_filter = ['ori_order_trade_no', 'creator', 'create_time']


class OrderListAdmin(object):
    readonly_fields = ['order', 'creator', 'create_time', 'update_time', 'is_delete']
    list_filter = ['order__trade_no', 'creator', 'create_time']


xadmin.site.register(CustomerInfo, CustomerInfoAdmin)
xadmin.site.register(CountIdList, CountIdListAdmin)
xadmin.site.register(OrderList, OrderListAdmin)

