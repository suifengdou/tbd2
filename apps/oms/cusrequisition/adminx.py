# -*- coding: utf-8 -*-
# @Time    : 2019/6/28 9:09
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

from .models import CusRequisitionInfo, CusRequisitionSubmitInfo
from apps.oms.planorderofpart.models import CusPartOrderInfo
from apps.wms.stock.models import StockInfo
from apps.wms.stockout.models import StockOutInfo
from apps.base.relationship.models import ManufactoryToWarehouse, GoodsToManufactoryInfo
from apps.oms.manuorder.models import ManuOrderInfo
from apps.base.goods.models import GoodsInfo


class CusPartOrderInfoInline(object):
    model = CusPartOrderInfo
    extra = 0
    exclude = ["creator", "planorder_id", "order_attribute", "status", "goods_name", "category", "manufactory"]

    def queryset(self):
        queryset = super(CusPartOrderInfoInline, self).queryset().filter(status=1)
        return queryset


class SubmitActionCR(BaseActionView):
    action_name = "submit_oriorder"
    description = "递交选中的需求单"
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
                queryset.update(status=3)
            else:
                num = 1
                for obj in queryset:
                    self.log('change', '', obj)
                    # 创建出库单
                    stockout_order = StockOutInfo()
                    stock_current = StockInfo.objects.filter(goods_id=obj.goods_id)
                    if stock_current:
                        available_quantity = stock_current[0].available_quantity()
                    else:
                        available_quantity = 0
                    if available_quantity < obj.quantity:
                        self.message_user("客供单号 %s 货品库存不足，请及时采购" % obj.cus_requisition_id, "error")
                        queryset.filter(cus_requisition_id=obj.cus_requisition_id).update(status=2)
                        continue
                    warehouse = ManufactoryToWarehouse.objects.filter(manufactory=obj.manufactory)
                    if warehouse:
                        stockout_order.warehouse = warehouse[0].warehouse
                    else:
                        self.message_user("客供单号 %s 工厂没有指定仓库，请先指定仓库。" % obj.cus_requisition_id, "error")
                        queryset.filter(cus_requisition_id=obj.cus_requisition_id).update(status=2)
                        continue

                    nickname = ManuOrderInfo.objects.filter(batch_num=obj.batch_num)
                    if nickname:
                        stockout_order.nickname = nickname[0].manufactory.name
                        stockout_order.city = nickname[0].manufactory.city
                        stockout_order.receiver = nickname[0].manufactory.contacts
                        stockout_order.mobile = nickname[0].manufactory.contacts_phone
                    else:
                        self.message_user("客供单号 %s 源生产订单出现错误，请查看生产订单状态。" % obj.cus_requisition_id, "error")
                        queryset.filter(cus_requisition_id=obj.cus_requisition_id).update(status=2)
                        continue

                    prefix = "SO"
                    serial_number = str(datetime.datetime.now())
                    serial_number = serial_number.replace("-", "").replace(" ", "").replace(":", "").replace(
                        ".", "")
                    serial_number = str(int(serial_number[0:15]) + num)
                    stockout_order.stockout_id = prefix + serial_number + "ACQ"
                    stockout_order.creator = self.request.user.username

                    stockout_order.source_order_id = obj.cus_requisition_id
                    stockout_order.category = 2

                    stockout_order.goods_name = obj.goods_name
                    stockout_order.goods_id = obj.goods_id
                    stockout_order.quantity = obj.quantity

                    try:
                        stockout_order.save()
                        queryset.filter(cus_requisition_id=obj.cus_requisition_id).update(status=3)
                        self.message_user("客供单号 %s 成功生成出库单。" % obj.cus_requisition_id, "success")
                    except Exception as e:
                        self.message_user("客供单号 %s 生成出库单错误，错误为：%s" % (obj.cus_requisition_id, e), "error")

            self.message_user("成功处理完毕 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')
        return None



class CusRequisitionInfoAdmin(object):
    list_display = ["cus_requisition_id", "planorder_id", "batch_num", "goods_id", "goods_name", "quantity", "available_quantity",
                    "estimated_time", "status", "manufactory"]
    list_filter = ["planorder_id", "batch_num", "goods_id", "goods_name", "status"]
    search_fields = ["planorder_id", "batch_num"]

    def has_add_permission(self):
        # 禁用添加按钮
        return False



class CusRequisitionSubmitInfoAdmin(object):
    list_display = ["cus_requisition_id", "planorder_id", "batch_num", "goods_id", "goods_name", "quantity", "available_quantity",
                    "estimated_time", "status", "manufactory"]

    actions = [SubmitActionCR, ]
    inlines = [CusPartOrderInfoInline, ]

    def queryset(self):
        qs = super(CusRequisitionSubmitInfoAdmin, self).queryset()
        qs = qs.filter(status__in=[1, 2])
        return qs

    def save_related(self):
        for i in range(self.formsets[0].forms.__len__()):
            request = self.request
            obj = self.org_obj

            prefix = "PP"
            serial_number = str(datetime.datetime.now())
            serial_number = int(serial_number.replace("-", "").replace(" ", "").replace(":", "").replace(".", "")) + i
            planorder_id = prefix + str(serial_number) + "ACR"
            self.formsets[0].forms[i].instance.planorder_id = planorder_id
            self.formsets[0].forms[i].instance.order_attribute = 1
            self.formsets[0].forms[i].instance.creator = request.user.username
            self.formsets[0].forms[i].instance.source_order_id = obj
            goods_name = GoodsInfo.objects.filter(goods_name=obj.goods_name)
            self.formsets[0].forms[i].instance.goods_name = goods_name[0]

            manufactory_part_qs = GoodsToManufactoryInfo.objects.filter(goods_name=goods_name[0])
            if manufactory_part_qs:
                self.formsets[0].forms[i].instance.manufactory = manufactory_part_qs[0].manufactory
            else:
                self.message_user(
                    "注意：订单 %s 配件 %s 没有关联工厂，需要请设置货品关联工厂" % (obj.planorder_id, self.formsets[0].forms[i].goods_name), 'error')

        super().save_related()


xadmin.site.register(CusRequisitionSubmitInfo, CusRequisitionSubmitInfoAdmin)
xadmin.site.register(CusRequisitionInfo, CusRequisitionInfoAdmin)