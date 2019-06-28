# -*- coding: utf-8 -*-
# @Time    : 2019/6/24 9:59
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


from .models import PlanOrderInfo, CusPartOrderInfo, CusRequisitionInfo, PlanOrderPenddingInfo, PlanOrderSubmitInfo, CusRequisitionSubmitInfo
from apps.oms.machine.models import GoodsInfo
from apps.oms.manuorder.models import ManuOrderInfo
from apps.base.relationship.models import GoodsToManufactoryInfo, PartToProductInfo, ManufactoryToWarehouse
from apps.wms.stock.models import StockOutInfo, StockInfo


class CusPartOrderInfoInline(object):
    model = CusPartOrderInfo
    extra = 0
    exclude = ["creator", "planorder_id", "order_attribute", "status", "goods_name", "category", "manufactory"]

    def queryset(self):
        queryset = super(CusPartOrderInfoInline, self).queryset().filter(status=1)
        return queryset


class CheckAction(BaseActionView):
    action_name = "submit_oriorder"
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
                queryset.update(status=2)
            else:
                for obj in queryset:
                    self.log('change', '', obj)
                    obj.update(status=2)
            self.message_user("成功审核 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


class SubmitActionPO(BaseActionView):
    action_name = "submit_oriorder"
    description = "递交选中的计划单"
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
                for obj in queryset:
                    self.log('change', '', obj)
                    # 创建工厂订单
                    manufactory_order = ManuOrderInfo()

                    estimated_time = obj.estimated_time
                    pre_year_num = int(datetime.datetime.strftime(estimated_time, "%Y")[-2:]) + 17
                    pre_week_num = int(datetime.datetime.strftime(estimated_time, "%U")) + 1
                    goods_number = obj.goods_name.goods_number
                    category = obj.goods_name.category

                    batch_tag = ["A", "B", "C", "D", "E", "F", "G"]
                    for tag in batch_tag:
                        batch_num = str(pre_year_num) + str(pre_week_num) + str(category) + str(goods_number) + str(tag)
                        if ManuOrderInfo.objects.filter(batch_num=batch_num).exists():
                            manufactory_order.batch_num = None
                            continue
                        else:
                            manufactory_order.batch_num = batch_num
                            break
                    if manufactory_order.batch_num is None:
                        self.message_user("存在异常订单 %s 请修正此订单之后再递交" % obj.planorder_id, "error")
                        queryset.filter(planorder_id=obj.planorder_id).update(status=3)
                        continue

                    if ManuOrderInfo.objects.filter(planorder_id=obj.planorder_id).exists():
                        self.message_user("此订单%s已经递交，请不要重复递交" % obj.planorder_id, "error")
                        queryset.filter(planorder_id=obj.planorder_id).update(status=3)
                        continue
                    else:
                        manufactory_order.planorder_id = obj.planorder_id

                    manufactory_machine_qs = GoodsToManufactoryInfo.objects.filter(goods_name=obj.goods_name)
                    if manufactory_machine_qs:
                        manufactory_order.manufactory = manufactory_machine_qs[0].manufactory
                    else:
                        self.message_user("此订单%s货品没有关联工程，请先设置货品关联工厂" % obj.planorder_id, "error")
                        queryset.filter(planorder_id=obj.planorder_id).update(status=3)
                        continue

                    manufactory_order.estimated_time = estimated_time
                    manufactory_order.goods_id = obj.goods_name.goods_id
                    manufactory_order.goods_name = obj.goods_name.goods_name
                    manufactory_order.quantity = obj.quantity
                    manufactory_order.start_sn = batch_num + str("00001")

                    transition_num = 100000 + int(obj.quantity)
                    manufactory_order.end_sn = batch_num + str(transition_num)[-5:]

                    try:
                        manufactory_order.save()
                        self.message_user("订单 %s 工厂订单创建完毕" % obj.planorder_id, 'success')
                        queryset.filter(planorder_id=obj.planorder_id).update(status=4)
                    except Exception as e:
                        self.message_user("订单 %s 创建错误，错误原因：%s" % (obj.planorder_id, e))
                        queryset.filter(planorder_id=obj.planorder_id).update(status=3)

                    # 创建客供需求单
                    parts_qs = PartToProductInfo.objects.filter(machine_name=obj.goods_name)
                    if parts_qs:
                        num = 1
                        for part in parts_qs:
                            customer_requisition = CusRequisitionInfo()

                            if CusRequisitionInfo.objects.filter(batch_num=batch_num, goods_id=customer_requisition.goods_id).exists():
                                self.message_user("此订单%s,此货品%s,已经创建需求单，请不要重复递交" % (obj.planorder_id, customer_requisition.goods_id))
                                continue

                            prefix = "CQ"
                            serial_number = str(datetime.datetime.now())
                            serial_number = serial_number.replace("-", "").replace(" ", "").replace(":", "").replace(
                                ".", "")
                            serial_number = str(int(serial_number[0:17]) + num)
                            customer_requisition.cus_requisition_id = prefix + serial_number + "A"
                            customer_requisition.creator = self.request.user.username

                            customer_requisition.planorder_id = obj.planorder_id
                            customer_requisition.batch_num = batch_num
                            customer_requisition.quantity = obj.quantity
                            customer_requisition.estimated_time = estimated_time
                            customer_requisition.goods_id = part.part_name.goods_id
                            customer_requisition.goods_name = part.part_name.goods_name

                            manufactory_part_qs = GoodsToManufactoryInfo.objects.filter(goods_name=part.part_name)
                            if manufactory_part_qs:
                                customer_requisition.manufactory = manufactory_part_qs[0].manufactory
                            else:
                                self.message_user("注意：订单 %s 配件 %s 没有关联工厂，需要请设置货品关联工厂" % (obj.planorder_id, customer_requisition.goods_name), 'error')

                            try:
                                customer_requisition.save()
                                self.message_user("订单 %s 客供需求货品%s订单创建完毕" % (obj.planorder_id, customer_requisition.goods_name), 'success')
                            except Exception as e:
                                self.message_user("此订单%s的客户需求单，创建出错，错误原因：%s" % (obj.planorder_id, e))
                            num += 1
                    else:
                        self.message_user("注意：订单 %s 生产的货品 %s 没有客供件" % (obj.planorder_id, obj.goods_name), 'error')

            self.message_user("成功处理完毕 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


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
                        available_inventory = stock_current[0].available_inventory()
                    else:
                        available_inventory = 0
                    if available_inventory < obj.quantity:
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


class PlanOrderInfoAdmin(object):
    list_display = ["planorder_id","goods_name","quantity","estimated_time","status","category","creator"]
    list_filter = ["goods_name", "category"]
    search_fields = ["planorder_id","goods_name"]
    readonly_fields = ["planorder_id","goods_name","quantity","estimated_time","status","category","creator"]


class PlanOrderPenddingInfoAdmin(object):
    list_display = ["planorder_id","goods_name","quantity","estimated_time","status","category","creator"]
    list_filter = ["goods_name", "category"]
    search_fields = ["planorder_id","goods_name"]

    actions = [CheckAction, ]

    def queryset(self):
        qs = super(PlanOrderPenddingInfoAdmin, self).queryset()
        qs = qs.filter(status=0)
        return qs

    def save_models(self):
        obj = self.new_obj
        request = self.request
        if obj.planorder_id is None:
            prefix = "PO"
            serial_number = str(datetime.datetime.now())
            serial_number = serial_number.replace("-", "").replace(" ", "").replace(":", "").replace(".", "")
            obj.planorder_id = prefix + str(serial_number)[0:17] + "A"
            obj.creator = request.user.username
            obj.save()
        super().save_models()


class PlanOrderSubmitInfoAdmin(object):
    list_display = ["planorder_id","goods_name","quantity","estimated_time","status","category","creator"]
    list_filter = ["goods_name", "category"]
    search_fields = ["planorder_id","goods_name"]
    actions = [SubmitActionPO, ]

    def queryset(self):
        qs = super(PlanOrderSubmitInfoAdmin, self).queryset()
        qs = qs.filter(status__in=[2, 3])
        return qs


class CusRequisitionInfoAdmin(object):
    list_display = ["cus_requisition_id", "planorder_id", "batch_num", "goods_id", "goods_name", "quantity", "available_inventory",
                    "estimated_time", "status", "manufactory"]
    list_filter = ["planorder_id", "batch_num", "goods_id", "goods_name", "status"]
    search_fields = ["planorder_id", "batch_num"]



class CusRequisitionSubmitInfoAdmin(object):
    list_display = ["cus_requisition_id", "planorder_id", "batch_num", "goods_id", "goods_name", "quantity", "available_inventory",
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


class CusPartOrderInfoAdmin(object):
    list_display = ["planorder_id", "goods_name", "quantity", "estimated_time", "status", "category", "order_attribute", "source_order_id", "manufactory"]




xadmin.site.register(PlanOrderPenddingInfo, PlanOrderPenddingInfoAdmin)
xadmin.site.register(PlanOrderSubmitInfo, PlanOrderSubmitInfoAdmin)
xadmin.site.register(PlanOrderInfo, PlanOrderInfoAdmin)
xadmin.site.register(CusRequisitionSubmitInfo, CusRequisitionSubmitInfoAdmin)
xadmin.site.register(CusRequisitionInfo, CusRequisitionInfoAdmin)
xadmin.site.register(CusPartOrderInfo, CusPartOrderInfoAdmin)



