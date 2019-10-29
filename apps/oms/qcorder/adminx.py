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
from apps.wms.stockin.models import StockInInfo
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
                queryset.update(order_status=3)
            else:
                i = 0
                for obj in queryset:
                    i += 1
                    self.log('change', '', obj)
                    accumulation = int(obj.batch_num.completednum()) + int(obj.batch_num.processingnum())
                    if accumulation > obj.batch_num.quantity:
                        self.message_user("此原始质检单号ID：%s，验货数量超过了订单数量，请修正" % obj.qc_order_id, "error")
                        queryset.filter(id=obj.id).update(order_status=2)
                        continue

                    stockin_order = StockInInfo()
                    warehouse_qs = ManufactoryToWarehouse.objects.filter(manufactory=obj.batch_num.manufactory)
                    if warehouse_qs:
                        warehouse = warehouse_qs[0].warehouse
                        stockin_order.warehouse = warehouse
                    else:
                        self.message_user("此原始质检单号ID：%s，工厂未关联仓库，请添加工厂关联到仓库" % obj.qc_order_id, "error")
                        queryset.filter(id=obj.id).update(order_status=2)
                        continue

                    prefix = "SI"
                    serial_number = str(datetime.datetime.now())
                    serial_number = int(serial_number.replace("-", "").replace(" ", "").replace(":", "").replace(".", "")[0:16])
                    serial_number += i
                    stockin_order.stockin_id = prefix + str(serial_number) + "AQC"

                    stockin_order.category = 0
                    stockin_order.batch_num = obj.batch_num.batch_num
                    stockin_order.planorder_id = obj.batch_num.planorder_id
                    stockin_order.goods_name = obj.batch_num.goods_name
                    stockin_order.goods_id = obj.batch_num.goods_id
                    stockin_order.quantity = obj.quantity
                    stockin_order.source_order_id = obj.qc_order_id

                    try:
                        if StockInInfo.objects.filter(source_order_id=obj.qc_order_id).exists():
                            self.message_user("单号ID：%s，已经生成过入库单，此次未生成入库单" % obj.qc_order_id, "error")
                            queryset.filter(id=obj.id).update(order_status=2)
                        elif obj.result == 1:
                            self.message_user("%s，验货失败，不生成入库单" % obj.qc_order_id, "success")
                        else:
                            stockin_order.save()
                            self.message_user("%s，生成入库单号：%s" % (obj.qc_order_id, stockin_order.stockin_id), "success")
                    except Exception as e:
                        self.message_user("此原始质检单号ID：%s，出现错误，错误原因：%s" % (obj.id, e), "error")
                        queryset.filter(id=obj.id).update(order_status=2)
                        continue

                    qc_order = QCInfo()
                    qc_order.qc_order_id = obj.qc_order_id
                    qc_order.manufactory = obj.batch_num.manufactory

                    qc_order.batch_num = stockin_order.batch_num
                    qc_order.goods_name = stockin_order.goods_name
                    qc_order.goods_id = stockin_order.goods_id
                    qc_order.quantity = stockin_order.quantity

                    qc_order.result = obj.result
                    qc_order.total_quantity = obj.batch_num.quantity
                    qc_order.accumulation = int(obj.batch_num.completednum()) + qc_order.quantity
                    qc_order.category = obj.category
                    qc_order.check_quantity = obj.check_quantity
                    qc_order.a_flaw = obj.a_flaw
                    qc_order.b1_flaw = obj.b1_flaw
                    qc_order.b2_flaw = obj.b2_flaw
                    qc_order.c_flaw = obj.c_flaw
                    qc_order.memorandum = obj.memorandum

                    try:
                        if QCInfo.objects.filter(qc_order_id=obj.qc_order_id).exists():
                            self.message_user("单号ID：%s，已经递交过质检单，此次未生成质检单" % obj.qc_order_id, "error")
                            queryset.filter(id=obj.id).update(order_status=2)
                        else:
                            qc_order.save()
                            queryset.filter(id=obj.id).update(order_status=3)
                            self.message_user("ID：%s，递交质检单成功" % obj.qc_order_id, "success")
                    except Exception as e:
                        self.message_user("此原始质检单号ID：%s，递交到质检单明细出现错误，错误原因：%s" % (obj.qc_order_id, e))
                        queryset.filter(id=obj.id).update(order_status=2)
                        continue

            self.message_user("成功审核 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


class QCOriInfoAdmin(object):
    list_display = ['creator', "qc_order_id", "order_status", "batch_num","quantity","result","category","check_quantity","a_flaw","b1_flaw","b2_flaw","c_flaw","memorandum"]
    search_fields = ["batch_num"]
    readonly_fields = ["order_status", "batch_num","quantity","result","category","check_quantity","a_flaw","b1_flaw","b2_flaw","c_flaw","memorandum", 'creator', "qc_order_id"]

    def has_add_permission(self):
        # 禁用添加按钮
        return False


class QCSubmitOriInfoAdmin(object):
    list_display = ['creator', "qc_order_id", "order_status", "batch_num","quantity","result","category","check_quantity","a_flaw","b1_flaw","b2_flaw","c_flaw","memorandum"]
    search_fields = ["batch_num"]
    readonly_fields = ['creator', "qc_order_id"]

    actions = [SubmitAction, ]

    def queryset(self):
        qs = super(QCSubmitOriInfoAdmin, self).queryset()
        qs = qs.filter(order_status__in=[1, 2])
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

    def has_add_permission(self):
        # 禁用添加按钮
        return False


class QCInfoAdmin(object):
    list_display = ["batch_num","qc_order_id","goods_name","order_status","manufactory","goods_id","quantity","total_quantity","accumulation","result","category","check_quantity","a_flaw","b1_flaw","b2_flaw","c_flaw","memorandum"]
    list_filter = ["goods_name", "manufactory", "goods_id", "category"]

    def has_add_permission(self):
        # 禁用添加按钮
        return False


xadmin.site.register(QCSubmitOriInfo, QCSubmitOriInfoAdmin)
xadmin.site.register(QCOriInfo, QCOriInfoAdmin)
xadmin.site.register(QCInfo, QCInfoAdmin)






