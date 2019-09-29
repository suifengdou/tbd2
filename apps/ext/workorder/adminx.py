# -*- coding: utf-8 -*-
# @Time    : 2019/6/24 10:19
# @Author  : Hann
# @Site    : 
# @File    : adminx.py
# @Software: PyCharm

import math
import datetime
from django.core.exceptions import PermissionDenied
from django.db.models import Q
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

from .models import WorkOrder, WorkOrderApp, WorkOrderAppRev, WorkOrderHandle, WorkOrderHandleSto, WorkOrderKeshen, WorkOrderMine

from apps.oms.qcorder.models import QCSubmitOriInfo
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
                if obj.order_status == 3:
                    obj.order_status -= 3
                    obj.save()
                    self.message_user("%s 取消成功" % obj.express_id, "success")
                elif obj.order_status in [1, 2, 4, 5]:
                    if obj.wo_category == 1 and obj.order_status == 4:
                        obj.order_status -= 2
                        obj.save()
                        self.message_user("%s 驳回上一级成功" % obj.express_id, "success")
                    else:
                        obj.order_status -= 1
                        obj.save()
                        if obj.order_status == 0:
                            self.message_user("%s 取消成功" % obj.express_id, "success")
                        else:
                            self.message_user("%s 驳回上一级成功" % obj.express_id, "success")
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


# 逆向工单提交
class SubmitReverseAction(BaseActionView):
    action_name = "submit_r_wo"
    description = "提交选中的工单"
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
                    obj.order_status = 2
                    obj.save()
                    self.message_user("%s 审核完毕，等待客户反馈" % obj.express_id, "info")

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


# 正向工单提交
class SubmitAction(BaseActionView):
    action_name = "submit_wo"
    description = "提交选中的工单"
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
                queryset.update(status=4)
            else:
                for obj in queryset:
                    self.log('change', '', obj)
                    obj.submit_time = datetime.datetime.now()
                    obj.order_status = 4
                    obj.save()
                    self.message_user("%s 审核完毕，等待快递反馈" % obj.express_id, "info")

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


# 逆向工单客服反馈
class FeedbackReverseAction(BaseActionView):
    action_name = "submit_feedback"
    description = "提交选中的工单"
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
                queryset.update(status=4)
            else:
                for obj in queryset:
                    self.log('change', '', obj)
                    if obj.feedback:
                        obj.submit_time = datetime.datetime.now()
                        obj.order_status = 4
                        obj.servicer = self.request.user.username
                        start_time = datetime.datetime.strptime(str(obj.create_time).split(".")[0], "%Y-%m-%d %H:%M:%S")
                        end_time = datetime.datetime.strptime(str(obj.submit_time).split(".")[0], "%Y-%m-%d %H:%M:%S")
                        d_value = end_time - start_time
                        days_seconds = d_value.days*3600
                        total_seconds = days_seconds + d_value.seconds
                        obj.services_interval = math.floor(total_seconds/60)
                        obj.save()
                        self.message_user("%s 审核完毕，等待客户反馈" % obj.express_id, "info")
                    else:
                        self.message_user("%s 未批复执行意见，请补充执行意见" % obj.express_id, "error")
                        n -= 1

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


# 工单快递反馈
class CheckExpressAction(BaseActionView):
    action_name = "submit_exp_check"
    description = "提交选中的工单"
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
                queryset.update(status=5)
            else:
                for obj in queryset:
                    self.log('change', '', obj)
                    if (obj.is_return == 1 and obj.return_express_id) or obj.is_return == 0:
                        obj.handle_time = datetime.datetime.now()
                        obj.handler = self.request.user.username
                        obj.order_status = 5
                        start_time = datetime.datetime.strptime(str(obj.submit_time).split(".")[0], "%Y-%m-%d %H:%M:%S")
                        end_time = datetime.datetime.strptime(str(obj.handle_time).split(".")[0], "%Y-%m-%d %H:%M:%S")
                        d_value = end_time - start_time
                        days_seconds = d_value.days * 3600
                        total_seconds = days_seconds + d_value.seconds
                        obj.express_interval = math.floor(total_seconds / 60)
                        obj.save()
                        self.message_user("%s 处理完毕，提交客户处理" % obj.express_id, "info")
                    else:
                        self.message_user("%s 退回订单没有填写退回单号，或者修改为货物不返回类型的工单" % obj.express_id, "error")
                        n -= 1

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


# 复核工单通过
class PassedAction(BaseActionView):
    action_name = "submit_pass"
    description = "提交选中的工单"
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
                queryset.update(status=6)
            else:
                for obj in queryset:
                    self.log('change', '', obj)
                    obj.submit_time = datetime.datetime.now()
                    obj.order_status = 6
                    obj.save()
                    self.message_user("%s 处理完毕，工单完结" % obj.express_id, "info")

            self.message_user("成功完成 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


# 逆向工单创建
class WorkOrderAppRevAdmin(object):
    list_display = ['company', 'express_id', 'information', 'category', 'create_time', 'creator', 'update_time']
    list_filter = ['creator']
    search_fields = ['express_id']
    form_layout = [
        Fieldset('必填信息',
                 'express_id', 'information', 'category',),
        Fieldset(None,
                 'submit_time', 'creator', 'services_interval', 'handler', 'handle_time','servicer',
                 'express_interval', 'feedback', 'return_express_id', 'order_status', 'wo_category',
                 'is_delete', 'is_losing', 'is_return', 'memo', 'company', **{"style": "display:None"}),
    ]
    readonly_fields = ['is_delete', 'is_losing', 'is_return', 'submit_time', 'creator', 'services_interval', 'handler',
                       'handle_time', 'servicer', 'express_interval', 'feedback', 'return_express_id', 'order_status',
                       'wo_category', 'memo']
    actions = [SubmitReverseAction, RejectSelectedAction]

    def save_models(self):
        obj = self.new_obj
        request = self.request
        obj.creator = request.user.username
        obj.order_status = 1
        obj.wo_category = 1
        obj.company = request.user.company
        obj.save()
        super().save_models()

    def queryset(self):
        queryset = super(WorkOrderAppRevAdmin, self).queryset()
        queryset = queryset.filter(order_status=1, is_delete=0, company=self.request.user.company)
        return queryset


# 正向工单创建
class WorkOrderAppAdmin(object):
    list_display = ['company', 'express_id', 'information', 'category', 'create_time', 'servicer', 'update_time']
    list_filter = ['servicer']
    search_fields = ['express_id']
    form_layout = [
        Fieldset('必填信息',
                 'express_id', 'information', 'category', 'company'),
        Fieldset(None,
                 'submit_time', 'creator', 'services_interval', 'handler', 'handle_time', 'servicer',
                 'express_interval', 'feedback', 'return_express_id', 'order_status', 'wo_category',
                 'is_delete', 'is_losing', 'is_return', 'memo', **{"style": "display:None"}),
    ]
    readonly_fields = ['is_delete', 'is_losing', 'is_return', 'submit_time', 'creator', 'services_interval', 'handler',
                       'handle_time', 'servicer', 'express_interval', 'feedback', 'return_express_id', 'order_status',
                       'wo_category', 'memo']
    actions = [SubmitAction, RejectSelectedAction]

    def save_models(self):
        obj = self.new_obj
        request = self.request
        obj.creator = request.user.username
        obj.servicer = request.user.username
        obj.order_status = 3
        obj.save()
        super().save_models()

    def queryset(self):
        queryset = super(WorkOrderAppAdmin, self).queryset()
        queryset = queryset.filter(order_status=3, is_delete=0)
        return queryset


# 客服工单审核
class WorkOrderHandleAdmin(object):
    list_display = ['company', 'express_id', 'feedback', 'category', 'information', 'create_time', 'creator', 'update_time']
    list_filter = ['category']
    search_fields = ['express_id']
    list_editable = ['feedback']
    readonly_fields = ['express_id', 'information', 'category', 'is_delete', 'is_losing', 'is_return', 'submit_time',
                       'creator', 'services_interval', 'handler', 'handle_time', 'servicer', 'express_interval',
                       'return_express_id', 'order_status', 'wo_category', 'company', 'memo']
    actions = [FeedbackReverseAction, RejectSelectedAction]

    def queryset(self):
        queryset = super(WorkOrderHandleAdmin, self).queryset()
        queryset = queryset.filter(order_status=2, is_delete=0)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 申通工单审核
class WorkOrderHandleStoAdmin(object):
    list_display = ['company', 'express_id', 'feedback', 'is_losing', 'is_return', 'return_express_id', 'information', 'category', 'create_time', 'servicer', 'submit_time']
    list_filter = ['category', 'submit_time']
    search_fields = ['express_id']
    list_editable = ['feedback', 'is_losing', 'is_return', 'return_express_id']
    readonly_fields = ['express_id', 'information', 'category', 'is_delete', 'submit_time', 'creator',
                       'services_interval', 'handler', 'handle_time', 'servicer', 'express_interval', 'order_status',
                       'wo_category', 'company', 'memo']
    ordering = ['-submit_time']
    actions = [CheckExpressAction, RejectSelectedAction]

    def queryset(self):
        queryset = super(WorkOrderHandleStoAdmin, self).queryset()
        queryset = queryset.filter(order_status=4, is_delete=0, company=self.request.user.company)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


class WorkOrderKeshenAdmin(object):
    list_display = ['company', 'is_return', 'express_id', 'return_express_id', 'feedback', 'is_losing', 'memo','information',
                    'category', 'create_time', 'servicer', 'submit_time', 'handle_time', 'handler']
    list_filter = ['company', 'is_return', 'is_losing']
    search_fields = ['return_express_id', 'express_id']
    list_editable = ['memo']
    readonly_fields = ['express_id', 'information', 'category', 'is_delete', 'is_losing', 'is_return', 'submit_time',
                       'creator', 'services_interval', 'handler', 'handle_time', 'servicer', 'express_interval',
                       'feedback', 'return_express_id', 'order_status', 'wo_category', 'company']
    actions = [PassedAction, RejectSelectedAction]

    def queryset(self):
        queryset = super(WorkOrderKeshenAdmin, self).queryset()
        queryset = queryset.filter(order_status=5, is_delete=0)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


class WorkOrderMineAdmin(object):
    list_display = ['order_status', 'company', 'is_return', 'return_express_id', 'feedback', 'is_losing', 'information',
                    'express_id', 'category', 'creator', 'servicer', 'handler']
    list_filter = ['submit_time', 'handle_time', 'is_return', 'is_losing', 'category']
    search_fields = ['express_id']
    readonly_fields = ['express_id', 'information', 'category', 'is_delete', 'is_losing', 'is_return', 'submit_time',
                       'creator', 'services_interval', 'handler', 'handle_time', 'servicer', 'express_interval',
                       'feedback', 'return_express_id', 'order_status', 'wo_category', 'company', 'memo']

    def queryset(self):
        queryset = super(WorkOrderMineAdmin, self).queryset()
        myname = self.request.user.username
        queryset = queryset.filter(Q(is_delete=0) & (Q(creator=myname) | Q(servicer=myname) | Q(handler=myname)))
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


class WorkOrderAdmin(object):
    list_display = ['order_status', 'company', 'is_return', 'return_express_id', 'feedback', 'is_losing', 'information',
                    'express_id', 'category', 'create_time', 'servicer', 'submit_time', 'handle_time', 'handler']
    list_filter = ['submit_time', 'handle_time', 'is_return', 'is_losing', 'category']
    search_fields = ['express_id']
    readonly_fields = ['express_id', 'information', 'category', 'is_delete', 'is_losing', 'is_return', 'submit_time',
                       'creator', 'services_interval', 'handler', 'handle_time', 'servicer', 'express_interval',
                       'feedback', 'return_express_id', 'order_status', 'wo_category', 'company', 'memo']

    def has_add_permission(self):
        # 禁用添加按钮
        return False

    def queryset(self):
        request = self.request
        if request.user.company is not None:

            if request.user.company.id == 1:
                queryset = super(WorkOrderAdmin, self).queryset()
                return queryset
            else:
                queryset = super(WorkOrderAdmin, self).queryset()
                queryset = queryset.filter(company=request.user.company)
                return queryset
        else:
            queryset = super(WorkOrderAdmin, self).queryset().filter(id=0)
            self.message_user("当前账号查询出错，当前账号没有设置公司，请联系管理员设置公司！！", "error")
            return queryset


xadmin.site.register(WorkOrderAppRev, WorkOrderAppRevAdmin)
xadmin.site.register(WorkOrderApp, WorkOrderAppAdmin)
xadmin.site.register(WorkOrderHandle, WorkOrderHandleAdmin)
xadmin.site.register(WorkOrderHandleSto, WorkOrderHandleStoAdmin)
xadmin.site.register(WorkOrderKeshen, WorkOrderKeshenAdmin)
xadmin.site.register(WorkOrderMine, WorkOrderMineAdmin)
xadmin.site.register(WorkOrder, WorkOrderAdmin)
