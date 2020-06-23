# -*- coding: utf-8 -*-
# @Time    : 2020/6/8 10:39
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

from .models import WorkOrder, WOCategory, WORCreate, WOPCreate, WORCheck, WOSCheck, WORFinish, WOPFinish


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
                obj.mistake_tag = 4
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
                        if re.match(r'^[A-Za-z0-9]+$', obj.express_id):
                            obj.order_status = 2
                            obj.mistake_tag = 0
                            if not obj.submit_time:
                                obj.submit_time = datetime.datetime.now()
                            obj.save()
                        else:
                            self.message_user("%s 物流单号错误" % obj.express_id, "error")
                            n -= 1
                            obj.mistake_tag = 1
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
                    if obj.wo_category == 1:
                        if obj.feedback:
                            obj.order_status = 3
                            obj.mistake_tag = 0
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
                            self.message_user("%s 反馈信息为空" % obj.express_id, "error")
                            n -= 1
                            obj.mistake_tag = 3
                            obj.save()
                            continue

                    elif obj.wo_category == 0:
                        if obj.servicer_feedback:
                            obj.order_status = 3
                            obj.mistake_tag = 0
                            obj.handle_time = datetime.datetime.now()
                            obj.servicer = self.request.user.username
                            start_time = datetime.datetime.strptime(str(obj.submit_time).split(".")[0],
                                                                    "%Y-%m-%d %H:%M:%S")
                            end_time = datetime.datetime.strptime(str(obj.handle_time).split(".")[0],
                                                                  "%Y-%m-%d %H:%M:%S")
                            d_value = end_time - start_time
                            days_seconds = d_value.days * 3600
                            total_seconds = days_seconds + d_value.seconds
                            obj.services_interval = math.floor(total_seconds / 60)
                            obj.save()
                        else:
                            self.message_user("%s 反馈信息为空" % obj.express_id, "error")
                            n -= 1
                            obj.mistake_tag = 3
                            obj.save()
                            continue
                    else:
                        self.message_user("%s 单据类型错误" % obj.express_id, "error")
                        n -= 1
                        obj.mistake_tag = 2
                        obj.save()
                        continue

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
                queryset.update(status=5)
            else:
                for obj in queryset:
                    self.log('change', '', obj)
                    if obj.wo_category == 1:
                        if obj.servicer_feedback:
                            obj.order_status = 4
                            obj.mistake_tag = 0
                            obj.save()
                        else:
                            self.message_user("%s 反馈信息为空" % obj.express_id, "error")
                            n -= 1
                            obj.mistake_tag = 3
                            obj.save()
                            continue

                    elif obj.wo_category == 0:
                        if obj.feedback:
                            obj.order_status = 4
                            obj.mistake_tag = 0
                            obj.save()
                        else:
                            self.message_user("%s 终审反馈信息为空" % obj.express_id, "error")
                            n -= 1
                            obj.mistake_tag = 3
                            obj.save()
                            continue
                    else:
                        self.message_user("%s 单据类型错误" % obj.express_id, "error")
                        n -= 1
                        obj.mistake_tag = 2
                        obj.save()
                        continue

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


# 维修工单类型界面
class WOCategoryAdmin(object):
    list_display = ['order_status', 'name']
    list_filter = []
    search_fields = []

    def save_models(self):
        obj = self.new_obj
        request = self.request
        if not obj.creator:
            obj.creator = request.user.username
            obj.save()
        super().save_models()


# 逆向创建维修工单界面
class WORCreateAdmin(object):
    list_display = ['category', 'mistake_tag', 'express_id', 'goods_name', 'information', 'creator',
                    'memo', 'process_tag', ]

    actions = [SubmitWOAction, RejectSelectedAction]

    form_layout = [
            Fieldset('关键信息',
                     Row('express_id', 'goods_name'),
                     Row('category',),),
            Fieldset('必填内容',
                     'information'),
            Fieldset(None,
                     'mistake_tag', 'submit_time', 'servicer', 'servicer_feedback', 'handler', 'services_interval',
                     'handle_time', 'process_interval', 'feedback', 'memo', 'order_status',
                     'creator', 'wo_category', 'process_tag', 'is_delete', **{"style": "display:None"})]

    def save_models(self):
        obj = self.new_obj
        request = self.request

        obj.creator = request.user.username
        obj.save()
        super().save_models()

    def queryset(self):
        queryset = super(WORCreateAdmin, self).queryset()
        queryset = queryset.filter(order_status=1, is_delete=0, wo_category=1)
        return queryset


# 正向创建维修工单界面
class WOPCreateAdmin(object):
    list_display = ['category', 'mistake_tag', 'express_id', 'goods_name', 'information', 'creator',
                    'memo', 'process_tag', ]

    actions = [SubmitWOAction, RejectSelectedAction]

    form_layout = [
            Fieldset('关键信息',
                     Row('express_id', 'goods_name'),
                     Row('category',),),
            Fieldset('必填内容',
                     'information'),
            Fieldset(None,
                     'mistake_tag', 'submit_time', 'servicer', 'servicer_feedback', 'handler', 'services_interval',
                     'handle_time', 'process_interval', 'feedback', 'memo', 'order_status',
                     'creator', 'wo_category', 'process_tag', 'is_delete', **{"style": "display:None"})]

    def save_models(self):
        obj = self.new_obj
        request = self.request

        obj.creator = request.user.username
        obj.wo_category = 0
        obj.save()
        super().save_models()

    def queryset(self):
        queryset = super(WOPCreateAdmin, self).queryset()
        queryset = queryset.filter(order_status=1, is_delete=0, wo_category=0)
        return queryset


# 客服审核维修工单界面
class WOSCheckAdmin(object):
    list_display = ['category', 'mistake_tag', 'express_id', 'goods_name', 'information', 'feedback',
                    'servicer_feedback', 'creator', 'memo', 'process_tag']
    list_editable = ['feedback', 'memo']
    readonly_fields = ['express_id', 'goods_name', 'information', 'submit_time', 'servicer', 'services_interval',
                       'servicer_feedback', 'handler', 'handle_time', 'process_interval',
                       'order_status', 'category', 'wo_category', 'process_tag', 'mistake_tag', 'creator',
                       'create_time', 'update_time', 'is_delete']
    search_fields = ['express_id', 'creator']
    actions = [CheckWOAction, RejectSelectedAction]

    def queryset(self):
        queryset = super(WOSCheckAdmin, self).queryset()
        queryset = queryset.filter(order_status=2, is_delete=0, wo_category=1)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 技术审核维修工单界面
class WORCheckAdmin(object):
    list_display = ['category', 'mistake_tag', 'express_id', 'goods_name', 'information', 'servicer_feedback',
                    'feedback', 'creator', 'memo', 'process_tag', ]
    list_editable = ['servicer_feedback', 'memo']
    readonly_fields = ['express_id', 'goods_name', 'information', 'submit_time', 'servicer', 'services_interval',
                       'handler', 'handle_time', 'process_interval', 'feedback',
                       'order_status', 'category', 'wo_category', 'process_tag', 'mistake_tag', 'creator',
                       'create_time', 'update_time', 'is_delete']
    search_fields = ['express_id', 'creator']
    actions = [CheckWOAction, RejectSelectedAction]

    def queryset(self):
        queryset = super(WORCheckAdmin, self).queryset()
        queryset = queryset.filter(order_status=2, is_delete=0, wo_category=0)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 技术终审界面
class WORFinishAdmin(object):
    list_display = ['category', 'mistake_tag', 'express_id', 'goods_name', 'information', 'feedback',
                     'servicer_feedback', 'creator', 'memo', 'process_tag', ]
    list_editable = ['servicer_feedback', 'memo']
    list_filter = ['category', 'mistake_tag', 'goods_name__goods_name']
    readonly_fields = ['express_id', 'goods_name', 'information', 'submit_time', 'servicer', 'services_interval',
                       'handler', 'handle_time', 'process_interval', 'feedback',
                       'order_status', 'category', 'wo_category', 'process_tag', 'mistake_tag', 'creator',
                       'create_time', 'update_time', 'is_delete']
    search_fields = ['express_id', 'creator']
    actions = [FinishWOAction, RejectSelectedAction]

    def queryset(self):
        queryset = super(WORFinishAdmin, self).queryset()
        queryset = queryset.filter(order_status=3, is_delete=0, wo_category=1)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 客服终审界面
class WOPFinishAdmin(object):
    list_display = ['category', 'mistake_tag', 'express_id', 'goods_name', 'information', 'servicer_feedback',
                    'feedback', 'creator', 'memo', 'process_tag', ]
    list_editable = ['feedback', 'memo']
    readonly_fields = ['express_id', 'goods_name', 'information', 'submit_time', 'servicer', 'services_interval',
                       'servicer_feedback', 'handler', 'handle_time', 'process_interval',
                       'order_status', 'category', 'wo_category', 'process_tag', 'mistake_tag', 'creator',
                       'create_time', 'update_time', 'is_delete']
    list_filter = ['category', 'mistake_tag', 'goods_name__goods_name']
    search_fields = ['express_id', 'creator']
    actions = [FinishWOAction, RejectSelectedAction]

    def queryset(self):
        queryset = super(WOPFinishAdmin, self).queryset()
        queryset = queryset.filter(order_status=3, is_delete=0, wo_category=0)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 维修工单查询
class WorkOrderAdmin(object):
    list_display = ['order_status', 'category', 'express_id', 'goods_name', 'information', 'creator',
                    'servicer_feedback', 'feedback', 'memo', 'process_tag', 'mistake_tag', 'wo_category']

    readonly_fields = ['express_id', 'goods_name', 'information', 'submit_time', 'servicer', 'services_interval',
                       'servicer_feedback', 'handler', 'handle_time', 'process_interval', 'feedback', 'memo',
                       'order_status', 'category', 'wo_category', 'process_tag', 'mistake_tag', 'creator',
                       'create_time', 'update_time', 'is_delete']
    list_filter = ['goods_name__goods_name', 'information', 'create_time', 'submit_time', 'handle_time', 'creator',
                   'order_status', 'category', 'wo_category',]
    search_fields = ['express_id']

    def has_add_permission(self):
        # 禁用添加按钮
        return False


xadmin.site.register(WOCategory, WOCategoryAdmin)
xadmin.site.register(WORCreate, WORCreateAdmin)
xadmin.site.register(WOPCreate, WOPCreateAdmin)
xadmin.site.register(WORCheck, WORCheckAdmin)
xadmin.site.register(WOSCheck, WOSCheckAdmin)
xadmin.site.register(WORFinish, WORFinishAdmin)
xadmin.site.register(WOPFinish, WOPFinishAdmin)
xadmin.site.register(WorkOrder, WorkOrderAdmin)

