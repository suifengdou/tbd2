# -*- coding: utf-8 -*-
# @Time    : 2019/6/24 10:20
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

from .models import QCOriInfo, QCInfo, QCSubmitOriInfo
from apps.wms.stock.models import StockInOrderInfo
from apps.base.relationship.models import ManufactoryToWarehouse



class SubmitAction(BaseActionView):
    action_name = "submit_oriorder"
    description = "递交选中的质检单"
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
                         '批量修改了 %(count)d %(items)s.' % {"count": n, "items": model_ngettext(self.opts, n)})
                queryset.update(status=2)
            else:
                for obj in queryset:
                    self.log('change', '', obj)
                    stockin_order = StockInOrderInfo()
                    warehouse_qs = ManufactoryToWarehouse.objects.filter(manufactory=obj.batch_num.manufactory)
                    if warehouse_qs:
                        warehouse = warehouse_qs[0].warehouse.warehouse_name
                        stockin_order.warehouse = warehouse
                    else:
                        self.message_user("此原始质检单号ID：%s，工厂未关联仓库，请添加工厂关联到仓库" % obj.id)
                        queryset.filter(id=obj.id).update(status=1)
                        continue

                    stockin_order.category = 0
                    stockin_order.batch_num = obj.batch_num.batch_num
                    stockin_order.planorder_id = obj.batch_num.planorder_id
                    stockin_order.goods_name = obj.batch_num.goods_name
                    stockin_order.goods_id = obj.batch_num.goods_id
                    stockin_order.quantity = obj.quantity
                    stockin_order.source_order_id = obj.qc_order_id

                    try:
                        stockin_order.save()
                    except Exception as e:
                        self.message_user("此原始质检单号ID：%s，出现错误，错误原因：%s" % (obj.id, e))
                        queryset.filter(id=obj.id).update(status=1)
                        continue

                    qc_order = QCInfo()
                    qc_order.order_id = obj.qc_order_id
                    qc_order.manufactory = obj.batch_num.manufactor

                    qc_order.batch_num = stockin_order.batch_num
                    qc_order.goods_name = stockin_order.goods_name
                    qc_order.goods_id = stockin_order.goods_id
                    qc_order.quantity = stockin_order.quantity

                    qc_order.result = obj.result
                    qc_order.total_quantity = obj.batch_num.quantity
                    qc_order.accumulation = obj.batch_num.completednum + qc_order.quantity
                    qc_order.category = obj.category
                    qc_order.check_quantity = obj.check_quantity
                    qc_order.a_flaw = obj.a_flaw
                    qc_order.b1_flaw = obj.b1_flaw
                    qc_order.b2_flaw = obj.b2_flaw
                    qc_order.c_flaw = obj.c_flaw
                    qc_order.memorandum = obj.memorandum

                    try:
                        stockin_order.save()
                    except Exception as e:
                        self.message_user("此原始质检单号ID：%s，递交到质检单明细出现错误，错误原因：%s" % (obj.id, e))
                        queryset.filter(id=obj.id).update(status=1)
                        continue

            self.message_user("成功审核 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


class QCOriInfoAdmin(object):
    list_display = ['creator', "qc_order_id", "status", "batch_num","quantity","result","category","check_quantity","a_flaw","b1_flaw","b2_flaw","c_flaw","memorandum"]
    search_fields = ["batch_num"]
    readonly_fields = ["status", "batch_num","quantity","result","category","check_quantity","a_flaw","b1_flaw","b2_flaw","c_flaw","memorandum", 'creator', "qc_order_id"]


class QCSubmitOriInfoAdmin(object):
    list_display = ['creator', "qc_order_id", "status", "batch_num","quantity","result","category","check_quantity","a_flaw","b1_flaw","b2_flaw","c_flaw","memorandum"]
    search_fields = ["batch_num"]
    readonly_fields = ['creator', "qc_order_id"]

    actions = [SubmitAction, ]

    def queryset(self):
        qs = super(QCSubmitOriInfoAdmin, self).queryset()
        qs = qs.filter(status__in=[0, 1])
        return qs

    def save_models(self):
        obj = self.new_obj
        request = self.request
        if obj.qc_order_id is None:
            prefix = "QC"
            serial_number = str(datetime.datetime.now())
            serial_number = serial_number.replace("-", "").replace(" ", "").replace(":", "").replace(".", "")
            obj.qc_order_id = prefix + serial_number[0:16] + "M"
            obj.creator = request.user.username
            obj.save()
        super().save_models()


class QCInfoAdmin(object):
    list_display = ["batch_num","qc_order_id","goods_name","status","manufactory","goods_id","quantity","total_quantity","accumulation","result","category","check_quantity","a_flaw","b1_flaw","b2_flaw","c_flaw","memorandum"]
    list_filter = ["goods_name", "manufactory", "goods_id", "category"]


xadmin.site.register(QCSubmitOriInfo, QCSubmitOriInfoAdmin)
xadmin.site.register(QCOriInfo, QCOriInfoAdmin)
xadmin.site.register(QCInfo, QCInfoAdmin)






