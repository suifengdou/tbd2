# -*- coding: utf-8 -*-
# @Time    : 2019/6/24 9:59
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

import pandas as pd
import xadmin
from xadmin.plugins.actions import BaseActionView
from xadmin.views.base import filter_hook
from xadmin.util import model_ngettext
from xadmin.layout import Fieldset

from .models import PlanOrderInfo, PlanOrderPenddingInfo, PlanOrderSubmitInfo

from apps.oms.manuorder.models import ManuOrderInfo
from apps.base.relationship.models import GoodsToManufactoryInfo, PartToProductInfo
from apps.oms.cusrequisition.models import CusRequisitionInfo


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
    def delete_models(self, queryset):
        n = queryset.count()
        if n:
            for obj in queryset:
                if obj.order_status == 1:
                    obj.order_status -= 1
                    obj.save()
                    self.message_user("%s 取消成功" % obj.planorder_id, "success")
                elif obj.order_status == 2:
                    obj.order_status -= 1
                    obj.save()
                    self.message_user("%s 驳回上一级成功" % obj.planorder_id, "success")
                elif obj.order_status == 3:
                    self.message_user("%s 已递交到工厂订单，驳回工厂订单，则自动驳回此计划单。" % obj.planorder_id, "success")
                    n -= 1
            self.message_user("成功驳回 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')
        return None

    @filter_hook
    def do_action(self, queryset):
        # Check that the user has delete permission for the actual model
        if not self.has_delete_permission():
            raise PermissionDenied

        using = router.db_for_write(self.model)

        # Populate deletable_objects, a data structure of all related objects that
        # will also be deleted.
        deletable_objects, model_count, perms_needed, protected = get_deleted_objects(
            queryset, self.opts, self.user, self.admin_site, using)

        # The user has already confirmed the deletion.
        # Do the deletion and return a None to display the change list view again.
        if self.request.POST.get('post'):
            if perms_needed:
                raise PermissionDenied
            self.delete_models(queryset)
            # Return None to display the change list page again.
            return None

        if len(queryset) == 1:
            objects_name = force_text(self.opts.verbose_name)
        else:
            objects_name = force_text(self.opts.verbose_name_plural)

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
                queryset.update(order_status=2)
            else:
                for obj in queryset:
                    self.log('change', '', obj)
                    obj.update(order_status=2)
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
                queryset.update(order_status=3)
            else:
                for obj in queryset:
                    self.log('change', '', obj)
                    manu_order = ManuOrderInfo.objects.filter(planorder_id=obj.planorder_id, order_status__in=[1, 2, 3, 4])
                    if manu_order.exists():
                        self.message_user("此订单%s已经存在工厂订单，请不要重复递交" % obj.planorder_id, "error")
                        continue
                    else:

                        # 创建工厂订单
                        manufactory_order = ManuOrderInfo()
                        manufactory_order.planorder_id = obj.planorder_id
                        estimated_time = obj.estimated_time
                        pre_year_num = int(datetime.datetime.strftime(estimated_time, "%Y")[-2:]) + 17
                        pre_week_num = int(datetime.datetime.strftime(estimated_time, "%U")) + 1
                        goods_number = obj.goods_name.goods_number
                        category = obj.goods_name.category

                        batch_tag = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N"]
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
                            continue

                        manufactory_machine_qs = GoodsToManufactoryInfo.objects.filter(goods_name=obj.goods_name)
                        if manufactory_machine_qs:
                            manufactory_order.manufactory = manufactory_machine_qs[0].manufactory
                        else:
                            self.message_user("此订单%s货品没有关联工程，请先设置货品关联工厂" % obj.planorder_id, "error")
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
                            queryset.filter(planorder_id=obj.planorder_id).update(order_status=3)
                        except Exception as e:
                            self.message_user("订单 %s 创建错误，错误原因：%s" % (obj.planorder_id, e))

                        # 创建客供需求单
                        parts_qs = PartToProductInfo.objects.filter(machine_name=obj.goods_name, status=1)
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

    def update_data(self, obj, target_obj):
        pass


class PlanOrderInfoAdmin(object):
    list_display = ["planorder_id","goods_name","quantity","estimated_time","order_status","category","creator"]
    list_filter = ["goods_name", "category"]
    search_fields = ["planorder_id","goods_name"]
    readonly_fields = ["planorder_id","goods_name","quantity","estimated_time","order_status","category","creator"]

    def has_add_permission(self):
        # 禁用添加按钮
        return False


class PlanOrderPenddingInfoAdmin(object):
    list_display = ["planorder_id","goods_name","quantity","estimated_time","order_status","category","creator"]
    list_filter = ["goods_name", "category"]
    search_fields = ["planorder_id","goods_name"]

    form_layout = [
        Fieldset('必填信息',
                 'planorder_id', 'goods_name', "estimated_time", "quantity", "category"),
        Fieldset(None,
                 'creator', 'order_status', 'is_delete', **{"style": "display:None"}),
    ]

    actions = [CheckAction, RejectSelectedAction]

    def queryset(self):
        qs = super(PlanOrderPenddingInfoAdmin, self).queryset()
        qs = qs.filter(order_status=1)
        return qs

    def save_models(self):
        obj = self.new_obj
        request = self.request
        obj.creator = request.user.username
        obj.save()
        if obj.planorder_id is None:
            prefix = "PO"
            serial_number = str(datetime.datetime.now())
            serial_number = serial_number.replace("-", "").replace(" ", "").replace(":", "").replace(".", "")
            obj.planorder_id = prefix + str(serial_number)[0:17] + "A"
            obj.save()
        super().save_models()


class PlanOrderSubmitInfoAdmin(object):
    list_display = ["planorder_id","goods_name","quantity","estimated_time","order_status","category","creator"]
    list_filter = ["goods_name", "category"]
    search_fields = ["planorder_id","goods_name"]
    actions = [SubmitActionPO, RejectSelectedAction]

    def queryset(self):
        qs = super(PlanOrderSubmitInfoAdmin, self).queryset()
        qs = qs.filter(order_status=2)
        return qs

    def has_add_permission(self):
        # 禁用添加按钮
        return False


xadmin.site.register(PlanOrderPenddingInfo, PlanOrderPenddingInfoAdmin)
xadmin.site.register(PlanOrderSubmitInfo, PlanOrderSubmitInfoAdmin)
xadmin.site.register(PlanOrderInfo, PlanOrderInfoAdmin)




