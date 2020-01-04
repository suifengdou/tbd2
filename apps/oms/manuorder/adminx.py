# -*- coding: utf-8 -*-
# @Time    : 2019/6/24 10:19
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


from .models import ManuOrderInfo, ManuOrderPenddingInfo, ManuOrderProcessingInfo
from apps.oms.qcorder.models import QCSubmitOriInfo, QCOriInfo
from apps.oms.cusrequisition.models import CusRequisitionInfo
from apps.oms.planorder.models import PlanOrderInfo

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
                if obj.order_status == 1:
                    obj.order_status -= 1
                    PlanOrderInfo.objects.filter(planorder_id=obj.planorder_id).update(order_status=2)
                    obj.save()
                    self.message_user("%s 工厂订单取消成功，已驳回到计划单待递交界面。" % obj.planorder_id, "success")
                elif obj.order_status == 2:
                    qc_tag = QCOriInfo.objects.filter(batch_num=obj, order_status__in=[1, 2])
                    if qc_tag:
                        self.message_user("%s 已经开始生产，不可以驳回。" % obj.planorder_id, 'error')
                        n -= 1
                    else:
                        obj.order_status -= 1
                        obj.save()
                        self.message_user("%s 工厂订单已驳回到待递交界面。" % obj.planorder_id, "success")
                else:
                    self.message_user("%s 订单已经开始生产，无法驳回。" % obj.planorder_id, "success")
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
                queryset.update(order_status=2)
            else:
                for obj in queryset:
                    self.log('change', '', obj)
                    requisition = CusRequisitionInfo.objects.filter(batch_num=obj.batch_num, order_status=1)
                    if requisition:
                        self.message_user("%s 有存在未完成的需求单，请及时处理" % obj.planorder_id, "error")

                    else:
                        queryset.filter(planorder_id=obj.planorder_id).update(order_status=2)
                        self.message_user("%s 审核完毕，等待生产" % obj.planorder_id, "info")

            self.message_user("成功审核 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


class QCOriInfoInline(object):

    model = QCSubmitOriInfo
    # exclude = ["order_status", "creator", "qc_order_id"]
    exclude = ["is_delete", 'creator', 'qc_order_id']
    extra = 0
    style = 'table'
    # list_display = ["order_status", "batch_num","quantity","result","category","check_quantity","a_flaw","b1_flaw","b2_flaw","c_flaw"]

    # def queryset(self):
    #     queryset = super(QCOriInfoInline, self).queryset().filter(order_status=1)
    #     return queryset


class ManuOrderInfoAdmin(object):
    list_display = ["batch_num","planorder_id","goods_id","goods_name","quantity","order_status","manufactory","estimated_time","start_sn", "end_sn"]
    list_filter = ["goods_id","goods_name","order_status","manufactory","estimated_time"]
    search_fields = ["batch_num","planorder_id"]
    readonly_fields = ["batch_num","planorder_id","goods_id","goods_name","quantity","order_status","manufactory","estimated_time","creator","start_sn", "end_sn"]

    def has_add_permission(self):
        # 禁用添加按钮
        return False


class ManuOrderPenddingInfoAdmin(object):
    list_display = ["batch_num","tag_sign","planorder_id","goods_id","goods_name","quantity","order_status","manufactory","estimated_time","creator","start_sn", "end_sn"]
    list_filter = ["tag_sign","goods_id", "goods_name", "manufactory", "estimated_time","create_time","update_time"]
    list_editable = ['tag_sign']
    search_fields = ["batch_num", "planorder_id"]
    readonly_fields = ["batch_num","planorder_id","goods_id","goods_name","creator"]
    actions = [CheckAction, RejectSelectedAction]

    def queryset(self):
        queryset = super(ManuOrderPenddingInfoAdmin, self).queryset()
        queryset = queryset.filter(order_status=1)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


class ManuOrderProcessingInfoAdmin(object):
    list_display = ["batch_num","tag_sign","planorder_id","goods_id", "order_status","estimated_time","creator", "manufactory", "goods_name", "quantity", "processingnum", "completednum", "intransitnum", "penddingnum", "failurenum", "start_sn", "end_sn"]
    list_filter = ["tag_sign","goods_id", "goods_name", "manufactory", "estimated_time","create_time","update_time"]
    list_editable = ['tag_sign']
    search_fields = ["batch_num", "planorder_id"]
    readonly_fields = ["batch_num","planorder_id","goods_id", "order_status","estimated_time","creator", "manufactory", "goods_name", "quantity", "processingnum", "completednum","intransitnum", "penddingnum", "failurenum", "start_sn", "end_sn"]
    inlines = [QCOriInfoInline, ]
    actions = [RejectSelectedAction, ]

    def queryset(self):
        queryset = super(ManuOrderProcessingInfoAdmin, self).queryset()
        queryset = queryset.filter(order_status__in=[2, 3])
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
