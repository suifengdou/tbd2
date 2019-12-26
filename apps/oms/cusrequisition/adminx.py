# -*- coding: utf-8 -*-
# @Time    : 2019/6/28 9:09
# @Author  : Hann
# @Site    : 
# @File    : adminx.py
# @Software: PyCharm
import datetime
from django.core.exceptions import PermissionDenied
from django.db import router
from django.utils.encoding import force_text
from django.template.response import TemplateResponse

from django.contrib.admin.utils import get_deleted_objects
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

ACTION_CHECKBOX_NAME = '_selected_action'


# 驳回审核
class RejectSelectedAction(BaseActionView):

    action_name = "reject_selected"
    description = '驳回选中的工单'

    delete_confirmation_template = None
    delete_selected_confirmation_template = None

    delete_models_batch = False

    model_perm = 'change'
    icon = 'fa fa-times'

    @filter_hook
    def reject_models(self, queryset):
        n = queryset.count()
        if n:
            for obj in queryset:
                if ManuOrderInfo.objects.filter(planorder_id=obj.planorder_id, order_status__in=[2, 3, 4]).exists():
                    self.message_user("%s 订单已经开始生产，无法驳回。" % obj.planorder_id, "error")
                    n -= 1
                elif obj.order_status == 1:
                    obj.order_status -= 1
                    obj.save()
                    self.message_user("%s 工厂需求订单取消成功。" % obj.planorder_id, "success")
                elif obj.order_status == 2:
                    obj.order_status -= 1
                    obj.save()
                    self.message_user("%s 工厂需求订单驳回成功。" % obj.planorder_id, "success")
                else:
                    self.message_user("%s 需求单状态错误无法驳回，请联系管理员。" % obj.planorder_id, "error")
                    n -= 1
            self.message_user("成功驳回 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')
        return None

    @filter_hook
    def do_action(self, queryset):
        # Check that the user has delete permission for the actual model
        if not self.has_change_permission():
            raise PermissionDenied

        using = router.db_for_write(self.model)

        # Populate deletable_objects, a data structure of all related objects that
        # will also be deleted.
        deletable_objects, model_count, perms_needed, protected = get_deleted_objects(
            queryset, self.opts, self.user, self.admin_site, using)

        # The user has already confirmed the deletion.
        # Do the deletion and return a None to display the change list view again.
        if self.request.POST.get('post'):
            if not self.has_change_permission():
                raise PermissionDenied
            self.reject_models(queryset)
            # Return None to display the change list page again.
            return None

        if len(queryset) == 1:
            objects_name = force_text(self.opts.verbose_name)
        else:
            objects_name = force_text(self.opts.verbose_name_plural)
        perms_needed = []
        if perms_needed or protected:
            title = "Cannot reject %(name)s" % {"name": objects_name}
        else:
            title = "Are you sure?"

        context = self.get_context()
        context.update({
            "title": title,
            "objects_name": objects_name,
            "deletable_objects": [deletable_objects],
            'queryset': queryset,
            "perms_lacking": perms_needed,
            "protected": protected,
            "opts": self.opts,
            "app_label": self.app_label,
            'action_checkbox_name': ACTION_CHECKBOX_NAME,
        })

        # Display the confirmation page
        return TemplateResponse(self.request, self.delete_selected_confirmation_template or
                                self.get_template_list('views/model_reject_selected_confirm.html'), context)


class CusPartOrderInfoInline(object):
    model = CusPartOrderInfo
    extra = 0
    exclude = ["creator", "planorder_id", "order_attribute", "order_status", "goods_name", "category", "manufactory"]

    def queryset(self):
        queryset = super(CusPartOrderInfoInline, self).queryset().filter(order_status=1)
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
                queryset.update(order_status=3)
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

                        continue
                    warehouse = ManufactoryToWarehouse.objects.filter(manufactory=obj.manufactory)
                    if warehouse:
                        stockout_order.warehouse = warehouse[0].warehouse
                        stockout_order.nickname = warehouse[0].warehouse.warehouse_name
                        stockout_order.city = warehouse[0].warehouse.city.city
                        stockout_order.receiver = warehouse[0].warehouse.receiver
                        stockout_order.mobile = warehouse[0].warehouse.mobile
                        stockout_order.address = warehouse[0].warehouse.address
                    else:
                        self.message_user("客供单号 %s 工厂没有指定仓库，请先指定仓库。" % obj.cus_requisition_id, "error")
                        n -= 1
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
                        queryset.filter(cus_requisition_id=obj.cus_requisition_id).update(order_status=2)
                        self.message_user("客供单号 %s 成功生成出库单。" % obj.cus_requisition_id, "success")
                    except Exception as e:
                        self.message_user("客供单号 %s 生成出库单错误，错误为：%s" % (obj.cus_requisition_id, e), "error")

            self.message_user("成功处理完毕 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')
        return None


class CusRequisitionInfoAdmin(object):
    list_display = ["cus_requisition_id", "planorder_id", "batch_num", "goods_id", "goods_name", "quantity", "available_quantity",
                    "estimated_time", "order_status", "manufactory"]
    list_filter = ["planorder_id", "batch_num", "goods_id", "goods_name", "order_status"]
    search_fields = ["planorder_id", "batch_num"]
    actions = [RejectSelectedAction, ]

    def has_add_permission(self):
        # 禁用添加按钮
        return False



class CusRequisitionSubmitInfoAdmin(object):
    list_display = ["cus_requisition_id", "planorder_id", "batch_num", "goods_id", "goods_name", "quantity", "available_quantity",
                    "estimated_time", "order_status", "manufactory"]

    actions = [SubmitActionCR, RejectSelectedAction]
    inlines = [CusPartOrderInfoInline, ]

    def queryset(self):
        qs = super(CusRequisitionSubmitInfoAdmin, self).queryset()
        qs = qs.filter(order_status=1)
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