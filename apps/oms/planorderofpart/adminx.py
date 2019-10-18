# -*- coding: utf-8 -*-
# @Time    : 2019/6/28 9:10
# @Author  : Hann
# @Site    : 
# @File    : adminx.py
# @Software: PyCharm

import datetime


from django.core.exceptions import PermissionDenied
import xadmin
from xadmin.plugins.actions import BaseActionView
from xadmin.views.base import filter_hook
from xadmin.util import model_ngettext


from .models import CusPartOrderInfo, CusPartPenddingOrderInfo, CusPartProductOrderInfo
from apps.wms.stockin.models import StockInInfo
from apps.base.relationship.models import ManufactoryToWarehouse


class CheckAction(BaseActionView):
    action_name = "check_pporder"
    description = "审核选中的计划单"
    model_perm = 'change'
    icon = "fa fa-flag"

    modify_models_batch = True

    @filter_hook
    def do_action(self, queryset):
        if not self.has_change_permission():
            raise PermissionDenied
        n = queryset.count()
        if n:
            if self.modify_models_batch:
                self.log('change',
                         '批量审核了 %(count)d %(items)s.' % {"count": n, "items": model_ngettext(self.opts, n)})
                queryset.update(order_status=2)
            else:
                for obj in queryset:
                    self.log('change', '', obj)
                    obj.update(order_status=2)
            self.message_user("成功审核 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


class SubmitAction(BaseActionView):
    action_name = "submit_pporder"
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
                queryset.update(order_status=3)
            else:
                i = 1
                for obj in queryset:
                    self.log('change', '', obj)
                    stockin_order = StockInInfo()

                    warehouse = ManufactoryToWarehouse.objects.filter(manufactory=obj.manufactory)
                    if warehouse:
                        stockin_order.warehouse = warehouse[0].warehouse
                    else:
                        self.message_user("%s 没有设置对应的仓库，请先设置对应的仓库" % obj.manufactory, 'error')
                        continue
                    stockin_order.source_order_id = obj.planorder_id
                    stockin_order.category = 1
                    stockin_order.goods_name = obj.goods_name.goods_name
                    stockin_order.goods_id = obj.goods_name.goods_id
                    stockin_order.quantity = obj.quantity

                    prefix = "SI"
                    serial_number = str(datetime.datetime.now())
                    serial_number = int(serial_number.replace("-", "").replace(" ", "").replace(":", "").replace(".", "")[0:16])
                    serial_number += i
                    stockin_order.stockin_id = prefix + str(serial_number) + "ACP"

                    try:
                        stockin_order.save()
                        self.message_user("%s 计划单入库单 %s 创建完毕" % (obj.planorder_id, stockin_order.stockin_id), 'success')
                        queryset.filter(id=obj.id).update(order_status=3)
                    except Exception as e:
                        self.message_user("%s 计划单出现错误，错误原因：%s" % (obj.planorder_id, e), 'error')

            self.message_user("成功审核 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


class CusPartOrderInfoAdmin(object):
    list_display = ["planorder_id", "goods_name", "quantity", "estimated_time", "order_status", "category", "order_attribute", "source_order_id", "manufactory"]

    def has_add_permission(self):
        # 禁用添加按钮
        return False


class CusPartPenddingOrderInfoAdmin(object):
    list_display = ["planorder_id", "goods_name", "quantity", "estimated_time", "order_status", "category", "order_attribute", "source_order_id", "manufactory"]
    actions = [CheckAction, ]

    def queryset(self):
        queryset = super(CusPartPenddingOrderInfoAdmin, self).queryset()
        queryset = queryset.filter(order_status=1)
        return queryset


class CusPartProductOrderInfoAdmin(object):
    list_display = ["planorder_id", "goods_name", "quantity", "estimated_time", "order_status", "category", "order_attribute",
                    "source_order_id", "manufactory"]
    actions = [SubmitAction, ]

    def queryset(self):
        queryset = super(CusPartProductOrderInfoAdmin, self).queryset()
        queryset = queryset.filter(order_status=2)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


xadmin.site.register(CusPartPenddingOrderInfo, CusPartPenddingOrderInfoAdmin)
xadmin.site.register(CusPartProductOrderInfo, CusPartProductOrderInfoAdmin)
xadmin.site.register(CusPartOrderInfo, CusPartOrderInfoAdmin)