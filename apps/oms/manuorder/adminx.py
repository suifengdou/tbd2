# -*- coding: utf-8 -*-
# @Time    : 2019/6/24 10:19
# @Author  : Hann
# @Site    : 
# @File    : adminx.py
# @Software: PyCharm

import datetime
from django.core.exceptions import PermissionDenied
import pandas as pd
import xadmin
from xadmin.plugins.actions import BaseActionView
from xadmin.views.base import filter_hook
from xadmin.util import model_ngettext


from .models import ManuOrderInfo, ManuOrderPenddingInfo, ManuOrderProcessingInfo
from apps.oms.qcorder.models import QCSubmitOriInfo


class QCOriInfoInline(object):

    model = QCSubmitOriInfo
    exclude = ["status", "creator", "qc_order_id"]
    extra = 0

    def queryset(self):
        queryset = super(QCOriInfoInline, self).queryset().filter(status=1)
        return queryset


class ManuOrderInfoAdmin(object):
    list_display = ["batch_num","planorder_id","goods_id","goods_name","quantity","status","manufactory","estimated_time","start_sn", "end_sn"]
    list_filter = ["goods_id","goods_name","status","manufactory","estimated_time"]
    search_fields = ["batch_num","planorder_id"]
    readonly_fields = ["batch_num","planorder_id","goods_id","goods_name","quantity","status","manufactory","estimated_time","creator","start_sn", "end_sn"]


class ManuOrderPenddingInfoAdmin(object):
    list_display = ["batch_num","planorder_id","goods_id","goods_name","quantity","status","manufactory","estimated_time","creator","start_sn", "end_sn"]
    list_filter = ["goods_id", "goods_name", "manufactory", "estimated_time"]
    search_fields = ["batch_num", "planorder_id"]
    readonly_fields = ["batch_num","planorder_id","goods_id","goods_name","creator"]

    def queryset(self):
        qs = super(ManuOrderPenddingInfoAdmin, self).queryset()
        qs = qs.filter(status=1)
        return qs


class ManuOrderProcessingInfoAdmin(object):
    list_display = ["batch_num","planorder_id","goods_id", "status","estimated_time","creator", "manufactory", "goods_name", "quantity", "completednum","start_sn", "end_sn"]
    list_filter = ["goods_id", "goods_name", "manufactory", "estimated_time"]
    search_fields = ["batch_num", "planorder_id"]
    readonly_fields = ["batch_num","planorder_id","goods_id", "status","estimated_time","creator", "manufactory", "goods_name", "quantity", "completednum","start_sn", "end_sn"]
    inlines = [QCOriInfoInline]

    def queryset(self):
        qs = super(ManuOrderProcessingInfoAdmin, self).queryset()
        qs = qs.filter(status__in=[2, 3])
        return qs

    def save_related(self):
        for i in range(self.formsets[0].forms.__len__()):
            request = self.request

            prefix = "QC"
            serial_number = str(datetime.datetime.now())
            serial_number = int(serial_number.replace("-", "").replace(" ", "").replace(":", "").replace(".", "")) + i
            qc_order_id = prefix + str(serial_number) + "A"
            self.formsets[0].forms[i].instance.planorder_id = qc_order_id
            self.formsets[0].forms[i].instance.creator = request.user.username
        super().save_related()


xadmin.site.register(ManuOrderPenddingInfo, ManuOrderPenddingInfoAdmin)
xadmin.site.register(ManuOrderProcessingInfo, ManuOrderProcessingInfoAdmin)
xadmin.site.register(ManuOrderInfo, ManuOrderInfoAdmin)
