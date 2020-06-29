# -*- coding: utf-8 -*-
# @Time    : 2020/6/29 8:27
# @Author  : Hann
# @Site    : 
# @File    : adminx.py
# @Software: PyCharm

import math, re
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
from xadmin.layout import Fieldset, Main, Row, Side

from .models import WorkOrder, WOCreate, WOCheck, WOFinish


ACTION_CHECKBOX_NAME = '_selected_action'


# 驳回审核
class RejectSelectedAction(BaseActionView):

    action_name = "reject_selected"
    description = '驳回工单'

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
                obj.order_status -= 1
                obj.mistake_tag = 2
                obj.process_tag = 0
                obj.save()
                if obj.order_status == 0:
                    self.message_user("%s 取消成功" % obj.id, "success")
                else:
                    self.message_user("%s 驳回上一级成功" % obj.id, "success")
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


# 递交
class SubmitWOAction(BaseActionView):
        action_name = "submit_wo"
        description = "提交工单"
        model_perm = 'change'
        icon = "fa fa-check-square-o"

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
                        if not obj.platform:
                            self.message_user("%s 平台错误，联系管理员设置账号" % obj.id, "error")
                            n -= 1
                            obj.mistake_tag = 4
                            obj.save()
                            continue
                        obj.order_status = 2
                        obj.mistake_tag = 0
                        if not obj.submit_time:
                            obj.submit_time = datetime.datetime.now()
                        obj.save()
                self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                                  'success')

            return None


# 审核
class CheckWOAction(BaseActionView):
    action_name = "check_wo"
    description = "审核工单"
    model_perm = 'change'
    icon = "fa fa-check-square-o"

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
                    if obj.feedback:
                        obj.order_status = 3
                        obj.mistake_tag = 0
                        obj.process_tag = 0
                        obj.handle_time = datetime.datetime.now()
                        obj.handler = self.request.user.username
                        start_time = datetime.datetime.strptime(str(obj.submit_time).split(".")[0],
                                                                "%Y-%m-%d %H:%M:%S")
                        end_time = datetime.datetime.strptime(str(obj.handle_time).split(".")[0],
                                                              "%Y-%m-%d %H:%M:%S")
                        d_value = end_time - start_time
                        days_seconds = d_value.days * 3600
                        total_seconds = days_seconds + d_value.seconds
                        obj.process_interval = math.floor(total_seconds / 60)
                        obj.save()
                    else:
                        self.message_user("%s 反馈信息为空" % obj.id, "error")
                        n -= 1
                        obj.mistake_tag = 1
                        obj.save()
                        continue

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


# 设置成待核实
class SetRCWOAction(BaseActionView):
    action_name = "setrc_wo"
    description = "工单设置成待核实"
    model_perm = 'change'
    icon = "fa fa-check-square-o"

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
                queryset.update(process_tag=1)
            else:
                for obj in queryset:
                    obj.process_tag = 1
                    obj.save()
            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


# 设置成待审批
class SetAPWOAction(BaseActionView):
    action_name = "setap_wo"
    description = "工单设置成待审批"
    model_perm = 'change'
    icon = "fa fa-check-square-o"

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
                queryset.update(process_tag=2)
            else:
                for obj in queryset:
                    obj.process_tag = 2
                    obj.save()
            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


# 确认解决
class ConfirmWOAction(BaseActionView):
    action_name = "confirm_wo"
    description = "确认解决工单"
    model_perm = 'change'
    icon = "fa fa-check-square-o"

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
                queryset.update(process_tag=3)
            else:
                for obj in queryset:
                    obj.process_tag = 3
                    obj.save()
            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


# 终审
class FinishWOAction(BaseActionView):
    action_name = "finish_wo"
    description = "终审工单"
    model_perm = 'change'
    icon = "fa fa-check-square-o"

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
                    if obj.process_tag != 3:
                        self.message_user("%s 反馈信息为空" % obj.id, "error")
                        n -= 1
                        obj.mistake_tag = 3
                        obj.save()
                        continue
                    self.log('change', '', obj)
                    if obj.servicer_feedback:
                        obj.order_status = 4
                        obj.mistake_tag = 0
                        obj.save()
                    else:
                        self.message_user("%s 反馈信息为空" % obj.id, "error")
                        n -= 1
                        obj.mistake_tag = 1
                        obj.save()
                        continue

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


class WOCreateAdmin(object):
    list_display = ['category', 'mistake_tag', 'information', 'creator', 'memo', 'process_tag']

    actions = [SubmitWOAction, RejectSelectedAction]

    form_layout = [
            Fieldset('关键信息',
                     'category', 'emergency_tag'),
            Fieldset('必填内容',
                     'information'),
            Fieldset(None,
                     'mistake_tag', 'submit_time', 'servicer', 'servicer_feedback', 'handler', 'services_interval',
                     'handle_time', 'process_interval', 'feedback', 'memo', 'order_status', 'platform',
                     'creator', 'process_tag', 'is_delete', **{"style": "display:None"})]

    def save_models(self):
        obj = self.new_obj
        request = self.request

        obj.creator = request.user.username
        if request.user.platform:
            obj.platform = request.user.platform
        else:
            self.message_user("联系管理员设置账号", "error")
            obj.mistake_tag = 4
        obj.save()
        super().save_models()

    def queryset(self):
        queryset = super(WOCreateAdmin, self).queryset()
        if self.request.user.is_superuser:
            queryset = queryset.filter(order_status=1, is_delete=0)
        else:
            queryset = queryset.filter(order_status=1, is_delete=0, creator=self.request.user.username)
        return queryset


class WOCheckAdmin(object):
    list_display = ['category', 'emergency_tag', 'mistake_tag', 'information', 'feedback',
                    'servicer_feedback', 'creator', 'memo', 'process_tag']
    list_editable = ['feedback', 'memo', ]
    readonly_fields = ['emergency_tag', 'information', 'submit_time', 'servicer', 'services_interval',
                       'servicer_feedback', 'handler', 'handle_time', 'process_interval', 'platform',
                       'order_status', 'category', 'process_tag', 'mistake_tag', 'creator',
                       'create_time', 'update_time', 'is_delete']
    list_filter = ['emergency_tag', 'category', 'creator', 'process_tag', 'mistake_tag', 'submit_time', 'create_time',]
    search_fields = ['creator']
    actions = [SetRCWOAction, SetAPWOAction, CheckWOAction, RejectSelectedAction]

    def queryset(self):
        queryset = super(WOCheckAdmin, self).queryset()
        if self.request.user.is_superuser:
            queryset = queryset.filter(order_status=2, is_delete=0)
        else:
            if self.request.user.platform:
                queryset = queryset.filter(order_status=2, is_delete=0, platform=self.request.user.platform)
            else:
                self.message_user("联系管理员设置账号", "error")
                queryset = queryset.filter(order_status=2, is_delete=1)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


class WOFinishAdmin(object):
    list_display = ['category', 'emergency_tag', 'mistake_tag', 'information', 'feedback',  'servicer_feedback',
                    'creator', 'memo', 'process_tag', ]
    list_editable = ['memo', 'servicer_feedback']
    readonly_fields = ['emergency_tag', 'information', 'submit_time', 'servicer', 'services_interval',
                       'servicer_feedback', 'handler', 'handle_time', 'process_interval', 'platform',
                       'order_status', 'category', 'process_tag', 'mistake_tag', 'creator',
                       'create_time', 'update_time', 'is_delete']
    list_filter = ['category', 'mistake_tag']
    search_fields = ['creator']
    actions = [ConfirmWOAction, FinishWOAction, RejectSelectedAction]

    def queryset(self):
        queryset = super(WOFinishAdmin, self).queryset()
        if self.request.user.is_superuser:
            queryset = queryset.filter(order_status=3, is_delete=0)
        else:
            queryset = queryset.filter(order_status=3, is_delete=0, creator=self.request.user.username)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


class WorkOrderAdmin(object):
    list_display = ['order_status', 'category', 'emergency_tag', 'information', 'creator',
                    'servicer_feedback', 'feedback', 'memo', 'process_tag', 'mistake_tag']

    readonly_fields = ['information', 'submit_time', 'servicer', 'services_interval',
                       'servicer_feedback', 'handler', 'handle_time', 'process_interval', 'feedback', 'memo',
                       'order_status', 'category', 'process_tag', 'mistake_tag', 'creator', 'platform', 'emergency_tag',
                       'create_time', 'update_time', 'is_delete']
    list_filter = ['platform', 'emergency_tag', 'information', 'create_time', 'submit_time', 'handle_time', 'creator',
                   'order_status', 'category', ]
    search_fields = ['creator']

    def has_add_permission(self):
        # 禁用添加按钮
        return False


xadmin.site.register(WOCreate, WOCreateAdmin)
xadmin.site.register(WOCheck, WOCheckAdmin)
xadmin.site.register(WOFinish, WOFinishAdmin)
xadmin.site.register(WorkOrder, WorkOrderAdmin)


