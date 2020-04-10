# coding: utf-8
# @Time : 2020/2/5 2:19 PM
# @Author: Hann
# @File: adminx.py

import datetime
from django.core.exceptions import PermissionDenied
from django.db import router
from django.utils.encoding import force_text
from django.template.response import TemplateResponse

from django.contrib.admin.utils import get_deleted_objects

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
from xadmin.layout import Fieldset

from .models import WorkOrder, WOCreate, WOService, WODealer, WOOperator, WOTrack



ACTION_CHECKBOX_NAME = '_selected_action'


# 驳回审核
class RejectAction(BaseActionView):

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

                obj.order_status -= 1
                obj.mistake_tag = 0
                obj.save()
                if obj.order_status == 0:
                    self.message_user("%s 取消成功" % obj.order_id, "success")
                else:
                    self.message_user("%s 驳回上一级成功" % obj.order_id, "success")

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


# 工单提交
class SubmitAction(BaseActionView):
    action_name = "submit_r_wo"
    description = "提交选中的工单"
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
                queryset.update(order_status=2)
            else:
                for obj in queryset:
                    self.log('change', '', obj)
                    obj.order_status = 2
                    obj.mistake_tag = 0
                    obj.create_time = datetime.datetime.now()
                    obj.save()
                    self.message_user("%s 审核完毕，等待客户反馈" % obj.order_id, "info")

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


# 客服处理工单提交
class SubmitServiceAction(BaseActionView):
    action_name = "submit_r_wo"
    description = "提交选中的工单"
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
                queryset.update(order_status=2)
            else:
                for obj in queryset:
                    if not obj.return_express_id:
                        self.message_user("%s 返回单号为空" % obj.order_id, "error")
                        obj.mistake_tag = 1
                        obj.save()
                        continue
                    if not obj.feedback:
                        self.message_user("%s 处理意见为空" % obj.order_id, "error")
                        obj.mistake_tag = 2
                        obj.save()
                        continue
                    if obj.process_tag != 6:
                        self.message_user("%s 先标记为已处理才能审核" % obj.order_id, "error")
                        obj.mistake_tag = 4
                        obj.save()
                        continue
                    self.log('change', '', obj)
                    obj.order_status = 3
                    obj.mistake_tag = 0
                    obj.submit_time = datetime.datetime.now()
                    obj.servicer = self.request.user.username
                    start_time = datetime.datetime.strptime(str(obj.create_time).split(".")[0], "%Y-%m-%d %H:%M:%S")
                    end_time = datetime.datetime.strptime(str(obj.submit_time).split(".")[0], "%Y-%m-%d %H:%M:%S")
                    d_value = end_time - start_time
                    days_seconds = d_value.days * 3600
                    total_seconds = days_seconds + d_value.seconds
                    obj.services_interval = math.floor(total_seconds / 60)
                    obj.save()
                    self.message_user("%s 审核完毕" % obj.order_id, "info")

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


# 工单批量设置顺丰
class SetSFAction(BaseActionView):
    action_name = "set_handlerYB"
    description = "批量设置顺丰快递"
    model_perm = 'change'
    icon = "fa fa-reply-all"

    modify_models_batch = False

    @filter_hook
    def do_action(self, queryset):
        if not self.has_change_permission():
            raise PermissionDenied
        n = queryset.count()
        if n:
            for obj in queryset:
                self.log('change', '', obj)
                if obj.is_customer_post == 1:
                    n -= 1
                    self.message_user("%s 客户寄回订单不可以更改快递" % obj.order_id, "error")
                    continue
                obj.return_express_company = '顺丰'
                obj.save()
                self.message_user("成功设置 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                                  'success')
        return None


# 工单批量设置处理中
class SetUHAction(BaseActionView):
    action_name = "set_unhandle"
    description = "批量设置处理中"
    model_perm = 'change'
    icon = "fa fa-reply-all"

    modify_models_batch = False

    @filter_hook
    def do_action(self, queryset):
        if not self.has_change_permission():
            raise PermissionDenied
        n = queryset.count()
        if n:
            for obj in queryset:
                self.log('change', '', obj)
                obj.process_tag = 1
                obj.save()
                self.message_user("成功设置 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                                  'success')
        return None


# 工单批量设置已处理
class SetHDAction(BaseActionView):
    action_name = "set_handled"
    description = "批量设置已处理"
    model_perm = 'change'
    icon = "fa fa-reply-all"

    modify_models_batch = False

    @filter_hook
    def do_action(self, queryset):
        if not self.has_change_permission():
            raise PermissionDenied
        n = queryset.count()
        if n:
            for obj in queryset:
                self.log('change', '', obj)
                obj.process_tag = 6
                obj.save()
                self.message_user("成功设置 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                                  'success')
        return None


# 经销商审核工单
class SubmitDealerAction(BaseActionView):
    action_name = "submit_dealer"
    description = "审核选中的工单"
    model_perm = 'change'
    icon = "fa fa-check-square-o"

    modify_models_batch = False

    @filter_hook
    def do_action(self, queryset):
        if not self.has_change_permission():
            raise PermissionDenied
        n = queryset.count()
        if n:
            for obj in queryset:
                self.log('change', '', obj)
                if not obj.memo:
                    n -= 1
                    self.message_user("%s 无经销商反馈" % obj.order_id, "error")
                    obj.mistake_tag = 3
                    obj.save()
                    continue
                if obj.process_tag != 7:
                    n -= 1
                    self.message_user("%s 先标记为终端清才能审核" % obj.order_id, "error")
                    obj.mistake_tag = 7
                    obj.save()
                    continue
                obj.order_status = 4
                obj.mistake_tag = 0
                obj.handle_time = datetime.datetime.now()
                obj.handler = self.request.user.username
                start_time = datetime.datetime.strptime(str(obj.submit_time).split(".")[0], "%Y-%m-%d %H:%M:%S")
                end_time = datetime.datetime.strptime(str(obj.handle_time).split(".")[0], "%Y-%m-%d %H:%M:%S")
                d_value = end_time - start_time
                days_seconds = d_value.days * 3600
                total_seconds = days_seconds + d_value.seconds
                obj.express_interval = math.floor(total_seconds / 60)
                obj.save()
                self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                                  'success')
        return None


# 经销商工单批量设置反馈意见为已确认
class SetMEAction(BaseActionView):
    action_name = "set_memo"
    description = "批量确认反馈意见"
    model_perm = 'change'
    icon = "fa fa-reply-all"

    modify_models_batch = False

    @filter_hook
    def do_action(self, queryset):
        if not self.has_change_permission():
            raise PermissionDenied
        n = queryset.count()
        if n:
            for obj in queryset:
                self.log('change', '', obj)
                obj.memo = '已确认'
                obj.save()
                self.message_user("成功设置 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                                  'success')
        return None


# 工单批量设置终端清
class SetFIAction(BaseActionView):
    action_name = "set_finished"
    description = "批量设置终端清"
    model_perm = 'change'
    icon = "fa fa-reply-all"

    modify_models_batch = False

    @filter_hook
    def do_action(self, queryset):
        if not self.has_change_permission():
            raise PermissionDenied
        n = queryset.count()
        if n:
            for obj in queryset:
                self.log('change', '', obj)
                obj.process_tag = 7
                obj.save()
                self.message_user("成功设置 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                                  'success')
        return None


# 运营审核工单
class SubmitOperatorAction(BaseActionView):
    action_name = "submit_operator"
    description = "审核选中的工单"
    model_perm = 'change'
    icon = "fa fa-check-square-o"

    modify_models_batch = False

    @filter_hook
    def do_action(self, queryset):
        if not self.has_change_permission():
            raise PermissionDenied
        n = queryset.count()
        if n:
            for obj in queryset:
                if obj.process_tag != 8:
                    n -= 1
                    self.message_user("%s 先标记为已对账才能审核" % obj.order_id, "error")
                    obj.mistake_tag = 5
                    obj.save()
                    continue
                self.log('change', '', obj)
                obj.order_status = 5
                obj.mistake_tag = 0
                obj.save()
                self.message_user("成功审核 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                                  'success')
        return None


# 运营批量设置已对账
class SetCHAction(BaseActionView):
    action_name = "set_check"
    description = "批量设置已对账"
    model_perm = 'change'
    icon = "fa fa-reply-all"

    modify_models_batch = False

    @filter_hook
    def do_action(self, queryset):
        if not self.has_change_permission():
            raise PermissionDenied
        n = queryset.count()
        if n:
            for obj in queryset:
                self.log('change', '', obj)
                obj.process_tag = 8
                obj.save()
                self.message_user("成功设置 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                                  'success')
        return None


# 恢复取消工单
class RecoverAction(BaseActionView):
    action_name = "recover"
    description = "恢复选中的工单"
    model_perm = 'change'
    icon = "fa fa-check-square-o"

    modify_models_batch = False

    @filter_hook
    def do_action(self, queryset):
        if not self.has_change_permission():
            raise PermissionDenied
        n = queryset.count()
        if n:
            for obj in queryset:
                if obj.order_status != 0:
                    n -= 1
                    self.message_user("%s 工单必须为取消状态" % obj.order_id, "error")
                    obj.mistake_tag = 6
                    obj.save()
                    continue
                self.log('change', '', obj)
                obj.order_status = 1
                obj.mistake_tag = 0
                obj.save()
                self.message_user("成功恢复 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                                  'success')
        return None


class WOCreateAdmin(object):
    list_display = ['company', 'order_id', 'information', 'feedback', 'memo', 'goods_name', 'quantity', 'amount', 'wo_category',
                    'is_customer_post', 'return_express_company', 'return_express_id', 'order_status','process_tag']
    list_filter = ['company__company_name', 'order_status', 'process_tag', 'create_time', 'update_time', 'goods_name__goods_name',
                   'quantity', 'amount', 'wo_category', 'is_losing', 'is_customer_post']

    search_fields = ['order_id', 'return_express_id']
    actions = [RejectAction, SubmitAction]
    list_editable = ['memo', 'quantity', 'amount']
    form_layout = [
        Fieldset('必填信息',
                 'order_id', 'information', 'goods_name', 'quantity', 'amount', 'wo_category',
                 'is_customer_post', 'return_express_company', 'return_express_id'),
        Fieldset(None,
                 'company', 'memo', 'submit_time', 'servicer', 'services_interval', 'is_losing', 'feedback', 'handler',
                 'handle_time', 'express_interval', 'order_status', 'is_delete', 'creator',
                 'process_tag','mistake_tag', 'platform', **{"style": "display:None"}),
    ]

    readonly_fields = ['feedback']

    def save_models(self):
        obj = self.new_obj
        request = self.request
        obj.creator = request.user.username
        obj.company = request.user.company
        obj.platform = request.user.platform
        obj.save()
        super().save_models()

    def queryset(self):
        queryset = super(WOCreateAdmin, self).queryset()
        if self.request.user.is_superuser == 1:
            queryset = queryset.filter(order_status=1, is_delete=0)
        else:
            queryset = queryset.filter(order_status=1, is_delete=0, creator=self.request.user.username)
        return queryset


class WOServiceAdmin(object):
    list_display = ['company', 'process_tag', 'mistake_tag', 'order_id', 'information', 'feedback', 'memo', 'goods_name', 'quantity',
                    'amount', 'wo_category', 'is_customer_post', 'return_express_company', 'return_express_id',
                    'submit_time', 'order_status']
    list_filter = ['process_tag', 'mistake_tag', 'company__company_name', 'order_status', 'create_time', 'update_time', 'goods_name__goods_name',
                   'quantity', 'amount', 'wo_category', 'is_losing', 'is_customer_post']

    search_fields = ['order_id', 'return_express_id']
    actions = [RejectAction, SubmitServiceAction, SetSFAction, SetUHAction, SetHDAction]
    list_editable = ['feedback', 'process_tag', 'return_express_company', 'return_express_id']

    form_layout = [
        Fieldset('必填信息',
                 'order_id', 'feedback', 'information', 'goods_name', 'quantity', 'amount', 'wo_category',
                 'is_customer_post', 'return_express_company', 'return_express_id'),
        Fieldset(None,
                 'company', 'memo', 'submit_time', 'servicer', 'services_interval',  'handler',
                 'handle_time', 'express_interval', 'order_status', 'is_delete', 'creator', 'platform', **{"style": "display:None"}),
    ]

    readonly_fields = ['company', 'order_id', 'information', 'memo', 'goods_name', 'quantity', 'amount', 'wo_category', 'platform',]

    def queryset(self):
        queryset = super(WOServiceAdmin, self).queryset()
        queryset = queryset.filter(order_status=2, is_delete=0, platform=self.request.user.platform)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 经销商工单界面
class WODealerAdmin(object):
    list_display = ['company', 'process_tag', 'mistake_tag', 'order_id', 'information', 'feedback', 'memo', 'goods_name', 'quantity',
                    'amount', 'wo_category', 'is_customer_post', 'return_express_company', 'return_express_id',
                    'submit_time', 'order_status']
    list_filter = ['process_tag', 'mistake_tag', 'company__company_name', 'order_status', 'process_tag', 'create_time', 'update_time', 'goods_name__goods_name',
                   'quantity', 'amount', 'wo_category', 'is_losing', 'is_customer_post']

    search_fields = ['order_id', 'return_express_id']
    actions = [RejectAction, SubmitDealerAction, SetMEAction, SetFIAction]
    list_editable = ['memo']
    form_layout = [
        Fieldset('必填信息',
                 'order_id', 'feedback', 'information', 'goods_name', 'quantity', 'amount', 'wo_category',
                 'is_customer_post', 'return_express_company', 'return_express_id'),
        Fieldset(None,
                 'company', 'memo', 'submit_time', 'servicer', 'services_interval',  'handler',
                 'handle_time', 'express_interval', 'order_status', 'is_delete', 'creator', 'platform', **{"style": "display:None"}),
    ]

    readonly_fields = ['company', 'order_id', 'information', 'feedback', 'process_tag', 'return_express_company', 'return_express_id', 'goods_name', 'quantity', 'amount', 'wo_category', 'platform',]

    def queryset(self):
        queryset = super(WODealerAdmin, self).queryset()
        if self.request.user.is_superuser == 1:
            queryset = queryset.filter(order_status=3, is_delete=0)
        else:
            queryset = queryset.filter(order_status=3, is_delete=0, creator=self.request.user.username)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 运营对账界面
class WOOperatorAdmin(object):
    list_display = ['order_id','order_status', 'process_tag', 'mistake_tag', 'company',  'information', 'feedback', 'memo', 'goods_name', 'quantity',
                    'amount', 'wo_category','return_express_company', 'return_express_id', 'submit_time', 'servicer',
                    'services_interval', 'is_losing', 'handler', 'handle_time', 'express_interval', 'process_tag']

    list_filter = ['process_tag', 'mistake_tag', 'company__company_name', 'order_status',  'create_time', 'update_time', 'goods_name__goods_name',
                   'quantity', 'amount', 'wo_category', 'is_losing', 'is_customer_post']

    search_fields = ['order_id', 'return_express_id']
    actions = [RejectAction, SubmitOperatorAction, SetCHAction]
    readonly_fields = ['order_id', 'information', 'feedback', 'memo', 'goods_name', 'quantity', 'amount', 'wo_category',
                       'is_customer_post', 'return_express_company', 'return_express_id', 'submit_time', 'servicer',
                       'services_interval', 'is_losing', 'handler', 'handle_time', 'express_interval', 'order_status',
                       'company', 'process_tag', 'platform',]

    def queryset(self):
        queryset = super(WOOperatorAdmin, self).queryset()
        if self.request.user.is_superuser == 1:
            queryset = queryset.filter(order_status=4, is_delete=0)
        else:
            queryset = queryset.filter(order_status=4, is_delete=0, company=self.request.user.company)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 单据追踪界面
class WOTrackAdmin(object):
    list_display = ['order_id','order_status', 'company',  'information', 'feedback', 'memo', 'goods_name', 'quantity',
                    'amount', 'wo_category','return_express_company', 'return_express_id', 'submit_time', 'servicer',
                    'services_interval', 'is_losing', 'handler', 'handle_time', 'express_interval', 'process_tag']

    list_filter = ['company__company_name', 'order_status', 'process_tag', 'create_time', 'update_time', 'goods_name__goods_name',
                   'quantity', 'amount', 'wo_category', 'is_losing', 'is_customer_post']

    search_fields = ['order_id', 'return_express_id']

    readonly_fields = ['order_id', 'information', 'feedback', 'memo', 'goods_name', 'quantity', 'amount', 'wo_category',
                       'is_customer_post', 'return_express_company', 'return_express_id', 'submit_time', 'servicer',
                       'services_interval', 'is_losing', 'handler', 'handle_time', 'express_interval', 'order_status',
                       'company', 'process_tag', 'mistake_tag', 'is_delete', 'platform',]

    def queryset(self):
        queryset = super(WOTrackAdmin, self).queryset()
        if self.request.user.is_superuser == 1:
            queryset = queryset.filter(order_status__in=[1, 2, 3, 4], is_delete=0)
        else:
            if self.request.user.company.company_name == '小狗吸尘器':
                queryset = queryset.filter(order_status__in=[1, 2, 3, 4], is_delete=0, platform=self.request.user.platform)
            else:
                if self.request.user.category == 1:

                    queryset = queryset.filter(order_status__in=[1, 2, 3, 4], is_delete=0, company=self.request.user.company)
                else:
                    queryset = queryset.filter(order_status__in=[1, 2, 3, 4], is_delete=0, creator=self.request.user.username)

        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


class WorkOrderAdmin(object):
    list_display = ['order_id','order_status', 'company',  'information', 'feedback', 'memo', 'goods_name', 'quantity',
                    'amount', 'wo_category','return_express_company', 'return_express_id', 'submit_time', 'servicer',
                    'services_interval', 'is_losing', 'handler', 'handle_time', 'express_interval', 'process_tag']

    list_filter = ['company__company_name', 'order_status', 'process_tag', 'create_time', 'update_time', 'goods_name__goods_name',
                   'quantity', 'amount', 'wo_category', 'is_losing', 'is_customer_post']
    actions = [RecoverAction, ]
    search_fields = ['order_id', 'return_express_id']

    readonly_fields = ['order_id', 'information', 'feedback', 'memo', 'goods_name', 'quantity', 'amount', 'wo_category',
                       'is_customer_post', 'return_express_company', 'return_express_id', 'submit_time', 'servicer',
                       'services_interval', 'is_losing', 'handler', 'handle_time', 'express_interval', 'order_status',
                       'company', 'process_tag', 'creator', 'mistake_tag', 'is_delete', 'platform',]

    def queryset(self):
        queryset = super(WorkOrderAdmin, self).queryset()
        if self.request.user.company.company_name == '小狗吸尘器':
            queryset = queryset.filter(is_delete=0, platform=self.request.user.platform)
        else:
            if self.request.user.category == 1:
                queryset = queryset.filter(is_delete=0, company=self.request.user.company)
            else:
                queryset = queryset.filter(is_delete=0, company=self.request.user.company, creator=self.request.user.username)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


xadmin.site.register(WOCreate, WOCreateAdmin)
xadmin.site.register(WOService, WOServiceAdmin)
xadmin.site.register(WODealer, WODealerAdmin)
xadmin.site.register(WOOperator, WOOperatorAdmin)
xadmin.site.register(WOTrack, WOTrackAdmin)
xadmin.site.register(WorkOrder, WorkOrderAdmin)