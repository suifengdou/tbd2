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
from apps.oms.cusrequisition.models import CusRequisitionInfo


class CheckAction(BaseActionView):
    action_name = "check_pporder"
    description = "审核选中的计划单"
    model_perm = 'change'
    icon = "fa fa-flag"

    modify_models_batch = False

    @filter_hook
    def do_action(self, queryset):
        if not self.has_change_permission():
            raise PermissionDenied
        n = queryset.count()
        if n:
            if self.modify_models_batch:
                self.log('change',
                         '批量审核了 %(count)d %(items)s.' % {"count": n, "items": model_ngettext(self.opts, n)})
                queryset.update(status=2)
            else:
                for obj in queryset:
                    self.log('change', '', obj)
                    requisition = CusRequisitionInfo.objects.filter(batch_num=obj.batch_num, status__in=[1, 2])
                    if requisition:
                        self.message_user("%s 有存在未完成的需求单，请及时处理" % obj.planorder_id, "error")
                        queryset.filter(planorder_id=obj.planorder_id).update(status=2)
                    else:
                        queryset.filter(planorder_id=obj.planorder_id).update(status=3)
                        self.message_user("%s 审核完毕，等待生产" % obj.planorder_id, "info")

            self.message_user("成功审核 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


class QCOriInfoInline(object):

    model = QCSubmitOriInfo
    exclude = ["status", "creator", "qc_order_id"]
    extra = 0

    def queryset(self):
        queryset = super(QCOriInfoInline, self).queryset().filter(status__in=[1, 2])
        return queryset


class ManuOrderInfoAdmin(object):
    list_display = ["batch_num","planorder_id","goods_id","goods_name","quantity","status","manufactory","estimated_time","start_sn", "end_sn"]
    list_filter = ["goods_id","goods_name","status","manufactory","estimated_time"]
    search_fields = ["batch_num","planorder_id"]
    readonly_fields = ["batch_num","planorder_id","goods_id","goods_name","quantity","status","manufactory","estimated_time","creator","start_sn", "end_sn"]

    def has_add_permission(self):
        # 禁用添加按钮
        return False


class ManuOrderPenddingInfoAdmin(object):
    list_display = ["batch_num","planorder_id","goods_id","goods_name","quantity","status","manufactory","estimated_time","creator","start_sn", "end_sn"]
    list_filter = ["goods_id", "goods_name", "manufactory", "estimated_time"]
    search_fields = ["batch_num", "planorder_id"]
    readonly_fields = ["batch_num","planorder_id","goods_id","goods_name","creator"]
    actions = [CheckAction, ]

    def queryset(self):
        queryset = super(ManuOrderPenddingInfoAdmin, self).queryset()
        queryset = queryset.filter(status__in=[1, 2])
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


class ManuOrderProcessingInfoAdmin(object):
    list_display = ["batch_num","planorder_id","goods_id", "status","estimated_time","creator", "manufactory", "goods_name", "quantity", "processingnum", "completednum", "intransitnum", "penddingnum", "failurenum", "start_sn", "end_sn"]
    list_filter = ["goods_id", "goods_name", "manufactory", "estimated_time"]
    search_fields = ["batch_num", "planorder_id"]
    readonly_fields = ["batch_num","planorder_id","goods_id", "status","estimated_time","creator", "manufactory", "goods_name", "quantity", "processingnum", "completednum","intransitnum", "penddingnum", "failurenum", "start_sn", "end_sn"]
    inlines = [QCOriInfoInline, ]

    def queryset(self):
        queryset = super(ManuOrderProcessingInfoAdmin, self).queryset()
        queryset = queryset.filter(status__in=[3, 4])
        return queryset

    def save_related(self):

        for i in range(self.formsets[0].forms.__len__()):
            request = self.request

            prefix = "QC"
            serial_number = str(datetime.datetime.now())
            serial_number = int(serial_number.replace("-", "").replace(" ", "").replace(":", "").replace(".", "")) + i
            qc_order_id = prefix + str(serial_number) + "A"
            self.formsets[0].forms[i].instance.qc_order_id = qc_order_id
            self.formsets[0].forms[i].instance.creator = request.user.username
        super().save_related()

        def has_add_permission(self):
            # 禁用添加按钮
            return False


xadmin.site.register(ManuOrderPenddingInfo, ManuOrderPenddingInfoAdmin)
xadmin.site.register(ManuOrderProcessingInfo, ManuOrderProcessingInfoAdmin)
xadmin.site.register(ManuOrderInfo, ManuOrderInfoAdmin)
