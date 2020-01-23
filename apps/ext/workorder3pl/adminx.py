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

from .models import WorkOrder3PL, WorkOrder3PLApp, WorkOrder3PLAppRev, WorkOrder3PLHandle, WorkOrder3PLHandleSto, WorkOrder3PLKeshen, WorkOrder3PLMine, WorkOrder3PLProcess


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
                if obj.order_status == 3:
                    obj.order_status -= 3
                    obj.save()
                    self.message_user("%s 取消成功" % obj.keyword, "success")
                elif obj.order_status in [1, 2, 4, 5, 6]:
                    if obj.wo_category == 1 and obj.order_status == 4:
                        obj.order_status -= 2
                        obj.save()
                        self.message_user("%s 驳回上一级成功" % obj.keyword, "success")
                    else:
                        obj.order_status -= 1
                        obj.save()
                        if obj.order_status == 0:
                            self.message_user("%s 取消成功" % obj.keyword, "success")
                        else:
                            self.message_user("%s 驳回上一级成功" % obj.keyword, "success")
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
                queryset.update(order_status=2)
            else:
                for obj in queryset:
                    self.log('change', '', obj)
                    obj.order_status = 2
                    obj.save()
                    self.message_user("%s 审核完毕，等待客户反馈" % obj.keyword, "info")

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
                queryset.update(order_status=4)
            else:
                for obj in queryset:
                    self.log('change', '', obj)
                    obj.submit_time = datetime.datetime.now()
                    obj.order_status = 4
                    obj.save()
                    self.message_user("%s 审核完毕，等待快递反馈" % obj.keyword, "info")

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
                queryset.update(order_status=4)
            else:
                for obj in queryset:
                    self.log('change', '', obj)
                    if obj.feedback:
                        obj.submit_time = datetime.datetime.now()
                        obj.order_status = 6
                        obj.servicer = self.request.user.username
                        start_time = datetime.datetime.strptime(str(obj.create_time).split(".")[0], "%Y-%m-%d %H:%M:%S")
                        end_time = datetime.datetime.strptime(str(obj.submit_time).split(".")[0], "%Y-%m-%d %H:%M:%S")
                        d_value = end_time - start_time
                        days_seconds = d_value.days*3600
                        total_seconds = days_seconds + d_value.seconds
                        obj.services_interval = math.floor(total_seconds/60)
                        obj.save()
                        self.message_user("%s 审核完毕，等待客户反馈" % obj.keyword, "info")
                    else:
                        self.message_user("%s 未批复执行意见，请补充执行意见" % obj.keyword, "error")
                        n -= 1

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


# 工单反馈
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
                queryset.update(order_status=5)
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
                        self.message_user("%s 处理完毕，提交客户处理" % obj.keyword, "info")
                    else:
                        self.message_user("%s 需要反馈的工单没有填写正向反馈内容，或者设置此工单为无需反馈！" % obj.keyword, "error")
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
                queryset.update(order_status=6)
            else:
                for obj in queryset:
                    self.log('change', '', obj)
                    obj.submit_time = datetime.datetime.now()
                    if obj.is_losing == 0:
                        obj.order_status = 7
                    else:
                        obj.order_status = 6
                    obj.save()
                    # self.message_user("%s 处理复核完毕" % obj.keyword, "info")

            self.message_user("成功完成 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


# 财审工单通过
class AuditAction(BaseActionView):
    action_name = "submit_audit"
    description = "提交选中的工单"
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
                queryset.update(order_status=7)
            else:
                for obj in queryset:
                    self.log('change', '', obj)
                    obj.submit_time = datetime.datetime.now()
                    if obj.is_losing == 0:
                        obj.order_status = 7
                    else:
                        obj.order_status = 6
                    obj.save()
                    self.message_user("%s 处理完毕，工单完结" % obj.keyword, "info")

            self.message_user("成功完成 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


# 逆向工单创建
class WorkOrder3PLAppRevAdmin(object):
    list_display = ['company', 'keyword', 'memo','information', 'category', 'create_time', 'creator', 'update_time']
    list_filter = ['creator', 'update_time', 'category']
    search_fields = ['express_id']
    form_layout = [
        Fieldset('必填信息',
                 'keyword', 'information', 'category',),
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
        queryset = super(WorkOrder3PLAppRevAdmin, self).queryset()
        queryset = queryset.filter(order_status=1, is_delete=0, company=self.request.user.company)
        return queryset


# 正向工单创建
class WorkOrder3PLAppAdmin(object):
    list_display = ['company', 'keyword', 'memo','information', 'category', 'create_time', 'servicer', 'update_time']
    list_filter = ['servicer', 'order_status', 'update_time', 'category']
    search_fields = ['keyword']
    form_layout = [
        Fieldset('必填信息',
                 'keyword', 'information', 'category', 'company'),
        Fieldset(None,
                 'submit_time', 'creator', 'services_interval', 'handler', 'handle_time', 'servicer',
                 'express_interval', 'feedback', 'return_express_id', 'order_status', 'wo_category',
                 'is_delete', 'is_losing', 'is_return', 'memo',  **{"style": "display:None"}),
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
        queryset = super(WorkOrder3PLAppAdmin, self).queryset()
        queryset = queryset.filter(order_status=3, is_delete=0)
        return queryset


# 客服工单审核
class WorkOrder3PLHandleAdmin(object):
    list_display = ['company', 'keyword', 'feedback', 'memo','category', 'information', 'create_time', 'creator', 'update_time']
    list_filter = ['category','servicer', 'order_status', 'update_time', 'category']
    search_fields = ['keyword']
    list_editable = ['feedback']
    readonly_fields = ['keyword', 'information', 'category', 'is_delete', 'is_losing', 'is_return', 'submit_time',
                       'creator', 'services_interval', 'handler', 'handle_time', 'servicer', 'express_interval',
                       'return_express_id', 'order_status', 'wo_category', 'company', 'memo']
    actions = [FeedbackReverseAction, RejectSelectedAction]

    def queryset(self):
        queryset = super(WorkOrder3PLHandleAdmin, self).queryset()
        queryset = queryset.filter(order_status=2, is_delete=0)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 工单审核
class WorkOrder3PLHandleStoAdmin(object):
    list_display = ['company', 'keyword', 'feedback', 'memo','is_losing', 'is_return', 'return_express_id', 'information', 'category', 'creator', 'create_time', 'servicer', 'submit_time']
    list_filter = ['category', 'submit_time','servicer', 'order_status', 'update_time']
    search_fields = ['keyword']
    list_editable = ['feedback', 'is_losing', 'is_return', 'return_express_id']
    readonly_fields = ['keyword', 'information', 'category', 'is_delete', 'submit_time', 'creator',
                       'services_interval', 'handler', 'handle_time', 'servicer', 'express_interval', 'order_status',
                       'wo_category', 'company', 'memo']
    ordering = ['-submit_time']
    actions = [CheckExpressAction, RejectSelectedAction]

    def queryset(self):
        queryset = super(WorkOrder3PLHandleStoAdmin, self).queryset()
        queryset = queryset.filter(order_status=4, is_delete=0, company=self.request.user.company)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


class WorkOrder3PLKeshenAdmin(object):
    list_display = ['company', 'is_return', 'keyword', 'return_express_id', 'feedback', 'memo','is_losing', 'information',
                    'category', 'create_time', 'servicer', 'submit_time', 'handle_time', 'handler']
    list_filter = ['company', 'is_return', 'is_losing','category', 'submit_time','servicer', 'order_status', 'update_time']
    search_fields = ['return_express_id', 'keyword']
    list_editable = ['memo']
    readonly_fields = ['keyword', 'information', 'category', 'is_delete', 'is_losing', 'is_return', 'submit_time',
                       'creator', 'services_interval', 'handler', 'handle_time', 'servicer', 'express_interval',
                       'feedback', 'return_express_id', 'order_status', 'wo_category', 'company']
    actions = [PassedAction, RejectSelectedAction]

    def queryset(self):
        queryset = super(WorkOrder3PLKeshenAdmin, self).queryset()
        queryset = queryset.filter(order_status=5, is_delete=0)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


class WorkOrder3PLMineAdmin(object):
    list_display = ['order_status', 'company', 'is_return', 'return_express_id', 'feedback', 'memo','is_losing', 'information',
                    'keyword', 'category', 'creator', 'servicer', 'handler']
    list_filter = ['submit_time', 'handle_time', 'is_return', 'is_losing', 'category', 'submit_time','servicer', 'order_status', 'update_time']
    search_fields = ['keyword']
    readonly_fields = ['keyword', 'information', 'category', 'is_delete', 'is_losing', 'is_return', 'submit_time',
                       'creator', 'services_interval', 'handler', 'handle_time', 'servicer', 'express_interval',
                       'feedback', 'return_express_id', 'order_status', 'wo_category', 'company', 'memo']
    actions = [AuditAction, RejectSelectedAction]

    def queryset(self):
        queryset = super(WorkOrder3PLMineAdmin, self).queryset()
        queryset = queryset.filter(is_delete=0, order_status=6)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 未完结工单查询
class WorkOrder3PLProcessAdmin(object):
    list_display = ['order_status', 'company', 'is_return', 'return_express_id', 'feedback', 'memo','is_losing', 'information',
                    'keyword', 'category', 'create_time', 'creator', 'servicer', 'submit_time', 'handle_time', 'handler']
    list_filter = ['order_status', 'create_time', 'creator', 'handle_time', 'is_return', 'is_losing', 'category']
    search_fields = ['keyword']
    readonly_fields = ['keyword', 'information', 'category', 'is_delete', 'is_losing', 'is_return', 'submit_time',
                       'creator', 'services_interval', 'handler', 'handle_time', 'servicer', 'express_interval',
                       'feedback', 'return_express_id', 'order_status', 'wo_category', 'company', 'memo']

    def has_add_permission(self):
        # 禁用添加按钮
        return False

    def queryset(self):
        request = self.request
        if request.user.company is not None:

            if request.user.company.company_name == '小狗电器':
                queryset = super(WorkOrder3PLProcessAdmin, self).queryset()
                queryset = queryset.filter(order_status__in=[1, 2, 3, 4, 5, 6])
                return queryset
            else:
                queryset = super(WorkOrder3PLProcessAdmin, self).queryset()
                queryset = queryset.filter(company=request.user.company, order_status__in=[1, 2, 3, 4, 5, 6])
                return queryset
        else:
            queryset = super(WorkOrder3PLProcessAdmin, self).queryset().filter(id=0)
            self.message_user("当前账号查询出错，当前账号没有设置公司，请联系管理员设置公司！！", "error")
            return queryset


# 工单查询
class WorkOrder3PLAdmin(object):
    list_display = ['order_status', 'company', 'is_return', 'return_express_id', 'feedback', 'memo','is_losing', 'information',
                    'keyword', 'category', 'create_time', 'creator', 'servicer', 'submit_time', 'handle_time', 'handler']
    list_filter = ['order_status', 'create_time', 'creator', 'handle_time', 'is_return', 'is_losing', 'category']
    search_fields = ['keyword']
    readonly_fields = ['keyword', 'information', 'category', 'is_delete', 'is_losing', 'is_return', 'submit_time',
                       'creator', 'services_interval', 'handler', 'handle_time', 'servicer', 'express_interval',
                       'feedback', 'return_express_id', 'order_status', 'wo_category', 'company', 'memo']

    def has_add_permission(self):
        # 禁用添加按钮
        return False

    def queryset(self):
        request = self.request
        if request.user.company is not None:

            if request.user.company.company_name == '小狗电器':
                queryset = super(WorkOrder3PLAdmin, self).queryset()
                return queryset
            else:
                queryset = super(WorkOrder3PLAdmin, self).queryset()
                queryset = queryset.filter(company=request.user.company)
                return queryset
        else:
            queryset = super(WorkOrder3PLAdmin, self).queryset().filter(id=0)
            self.message_user("当前账号查询出错，当前账号没有设置公司，请联系管理员设置公司！！", "error")
            return queryset


xadmin.site.register(WorkOrder3PLAppRev, WorkOrder3PLAppRevAdmin)
xadmin.site.register(WorkOrder3PLApp, WorkOrder3PLAppAdmin)
xadmin.site.register(WorkOrder3PLHandle, WorkOrder3PLHandleAdmin)
xadmin.site.register(WorkOrder3PLHandleSto, WorkOrder3PLHandleStoAdmin)
xadmin.site.register(WorkOrder3PLKeshen, WorkOrder3PLKeshenAdmin)
xadmin.site.register(WorkOrder3PLMine, WorkOrder3PLMineAdmin)
xadmin.site.register(WorkOrder3PLProcess, WorkOrder3PLProcessAdmin)
xadmin.site.register(WorkOrder3PL, WorkOrder3PLAdmin)
