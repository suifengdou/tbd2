# -*- coding: utf-8 -*-
# @Time    : 2019/6/24 10:20
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


from .models import QCOriInfo, QCInfo, QCSubmitOriInfo, QCSubmitInfo
from apps.wms.stockin.models import StockInInfo
from apps.base.relationship.models import ManufactoryToWarehouse

ACTION_CHECKBOX_NAME = '_selected_action'


# 原始质检单驳回审核
class RejectSelectedOriQCAction(BaseActionView):

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
                    self.message_user("%s 取消成功" % obj.qc_order_id, "success")
                elif obj.order_status == 2:
                    obj.order_status -= 1
                    obj.save()
                    self.message_user("%s 驳回上一级成功" % obj.qc_order_id, "success")
                elif obj.order_status == 3:
                    self.message_user("%s 已递交完成，请去验货明细表中驳回。" % obj.qc_order_id, "success")
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


# 质检单驳回审核
class RejectSelectedQCAction(BaseActionView):

    action_name = "reject_selected"
    description = '驳回选中的质检单'

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
                    ori_order = QCOriInfo.objects.filter(qc_order_id=obj.qc_order_id)[0]
                    ori_order.order_status = 1
                    ori_order.save()
                    obj.memorandum = "%s 取消了质检单号为：%s的质检单" % (str(self.request.user.username), obj.qc_order_id)
                    obj.qc_order_id = "DD" + str(datetime.datetime.now()).replace("-", "").replace(" ", "").replace(":", "").replace(".", "")[:14]
                    obj.order_status -= 1
                    obj.save()
                    self.message_user("%s 取消成功，原始质检单驳回到待递交界面" % obj.qc_order_id, "success")
                elif obj.order_status == 2:
                    self.message_user("%s 已递交完成，请去入库明细表中驳回。" % obj.qc_order_id, "success")
                    n -= 1
                else:
                    self.message_user("%s 内部错误，请联系管理员。" % obj.qc_order_id, "success")
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
                        continue

                    qc_order = QCInfo()
                    warehouse_qs = ManufactoryToWarehouse.objects.filter(manufactory=obj.batch_num.manufactory)
                    if warehouse_qs:
                        warehouse = warehouse_qs[0].warehouse
                        qc_order.warehouse = warehouse
                    else:
                        self.message_user("此原始质检单号ID：%s，工厂未关联仓库，请添加工厂关联到仓库" % obj.qc_order_id, "error")
                        continue

                    qc_order.qc_order_id = obj.qc_order_id
                    qc_order.manufactory = obj.batch_num.manufactory
                    qc_order.qc_time = obj.qc_time.strftime("%Y-%m-%d")
                    qc_order.batch_num = obj.batch_num
                    qc_order.goods_name = obj.batch_num.goods_name
                    qc_order.goods_id = obj.batch_num.goods_id
                    qc_order.quantity = obj.quantity

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
                            n -= 1
                            obj.order_status = 2
                            obj.save()
                            continue
                        else:
                            qc_order.save()
                            queryset.filter(id=obj.id).update(order_status=2)
                            self.message_user("ID：%s，递交质检单成功" % obj.qc_order_id, "success")
                    except Exception as e:
                        self.message_user("此原始质检单号ID：%s，递交到质检单明细出现错误，错误原因：%s" % (obj.qc_order_id, e))
                        continue

            self.message_user("成功审核 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


class SubmitSockInAction(BaseActionView):
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
                        continue
                    if StockInInfo.objects.filter(source_order_id=obj.qc_order_id, order_status__in=[1, 2]).exists():
                        self.message_user("单号ID：%s，已经生成过入库单，此次未生成入库单" % obj.qc_order_id, "error")
                        n -= 1
                        obj.order_status = 2
                        obj.save()
                        continue
                    stockin_order = StockInInfo()
                    warehouse_qs = ManufactoryToWarehouse.objects.filter(manufactory=obj.batch_num.manufactory)
                    if warehouse_qs:
                        warehouse = warehouse_qs[0].warehouse
                        stockin_order.warehouse = warehouse
                    else:
                        self.message_user("此原始质检单号ID：%s，工厂未关联仓库，请添加工厂关联到仓库" % obj.qc_order_id, "error")
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
                        if obj.result == 1:
                            self.message_user("%s，验货失败质检单，不生成入库单" % obj.qc_order_id, "success")
                            n -= 1
                            obj.order_status = 2
                            obj.save()
                            continue
                        else:
                            stockin_order.save()
                            self.message_user("%s，生成入库单号：%s" % (obj.qc_order_id, stockin_order.stockin_id), "success")
                            obj.order_status = 2
                            obj.save()
                            continue
                    except Exception as e:
                        self.message_user("此原始质检单号ID：%s，出现错误， ：%s" % (obj.id, e), "error")
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

    actions = [SubmitAction, RejectSelectedOriQCAction]

    def queryset(self):
        qs = super(QCSubmitOriInfoAdmin, self).queryset()
        qs = qs.filter(order_status=1)
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


class QCSubmitInfoAdmin(object):
    list_display = ["batch_num", "qc_order_id", "goods_name", "order_status", "manufactory", "goods_id", "quantity",
                    "total_quantity", "accumulation", "result", "category", "check_quantity", "a_flaw", "b1_flaw",
                    "b2_flaw", "c_flaw", "memorandum"]
    list_filter = ["goods_name", "manufactory", "goods_id", "category"]
    actions = [SubmitSockInAction, RejectSelectedQCAction]

    def queryset(self):
        qs = super(QCSubmitInfoAdmin, self).queryset()
        qs= qs.filter(order_status=1)
        return qs

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
xadmin.site.register(QCSubmitInfo, QCSubmitInfoAdmin)
xadmin.site.register(QCInfo, QCInfoAdmin)






