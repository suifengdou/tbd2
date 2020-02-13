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
                    self.log('change', '', obj)
                    obj.order_status = 2
                    obj.save()
                    self.message_user("%s 审核完毕，等待客户反馈" % obj.order_id, "info")

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
                self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                                  'success')
        return None


class WOCreateAdmin(object):
    list_display = ['company', 'order_id', 'information', 'feedback', 'memo', 'goods_name', 'quantity', 'amount', 'wo_category',
                    'is_customer_post', 'return_express_company', 'return_express_id', 'order_status','process_tag']
    list_filter = ['company', 'order_status', 'process_tag', 'create_time', 'update_time', 'goods_name__goods_name',
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
                 'process_tag', **{"style": "display:None"}),
    ]

    readonly_fields = ['feedback']

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
        queryset = super(WOCreateAdmin, self).queryset()
        queryset = queryset.filter(order_status=1, is_delete=0, company=self.request.user.company)
        return queryset


class WOServiceAdmin(object):
    list_display = ['company', 'process_tag', 'order_id', 'information', 'feedback', 'memo', 'goods_name', 'quantity',
                    'amount', 'wo_category', 'is_customer_post', 'return_express_company', 'return_express_id',
                    'submit_time', 'order_status']
    list_filter = ['company', 'order_status', 'process_tag', 'create_time', 'update_time', 'goods_name__goods_name',
                   'quantity', 'amount', 'wo_category', 'is_losing', 'is_customer_post']

    search_fields = ['order_id', 'return_express_id']
    actions = [RejectAction, SubmitServiceAction, SetSFAction]
    list_editable = ['feedback', 'process_tag', 'return_express_company', 'return_express_id']
    form_layout = [
        Fieldset('必填信息',
                 'order_id', 'feedback', 'information', 'goods_name', 'quantity', 'amount', 'wo_category',
                 'is_customer_post', 'return_express_company', 'return_express_id'),
        Fieldset(None,
                 'company', 'memo', 'submit_time', 'servicer', 'services_interval',  'handler',
                 'handle_time', 'express_interval', 'order_status', 'is_delete', 'creator', **{"style": "display:None"}),
    ]

    readonly_fields = ['company', 'order_id', 'information', 'memo', 'goods_name', 'quantity', 'amount', 'wo_category']


    def queryset(self):
        queryset = super(WOServiceAdmin, self).queryset()
        queryset = queryset.filter(order_status=1, is_delete=0)
        return queryset


class WODealerAdmin(object):
    pass


class WOOperatorAdmin(object):
    pass


class WOTrackAdmin(object):
    pass


class WorkOrderAdmin(object):
    list_display = ['order_id','order_status', 'company',  'information', 'feedback', 'memo', 'goods_name', 'quantity',
                    'amount', 'wo_category','return_express_company', 'return_express_id', 'submit_time', 'servicer',
                    'services_interval', 'is_losing', 'handler', 'handle_time', 'express_interval', 'process_tag']

    list_filter = ['company', 'order_status', 'process_tag', 'create_time', 'update_time', 'goods_name__goods_name',
                   'quantity', 'amount', 'wo_category', 'is_losing', 'is_customer_post']

    search_fields = ['order_id', 'return_express_id']

    readonly_fields = ['order_id', 'information', 'feedback', 'memo', 'goods_name', 'quantity', 'amount', 'wo_category',
                       'is_customer_post', 'return_express_company', 'return_express_id', 'submit_time', 'servicer',
                       'services_interval', 'is_losing', 'handler', 'handle_time', 'express_interval', 'order_status',
                       'company', 'process_tag']


xadmin.site.register(WOCreate, WOCreateAdmin)
xadmin.site.register(WOService, WOServiceAdmin)
xadmin.site.register(WODealer, WODealerAdmin)
xadmin.site.register(WOOperator, WOOperatorAdmin)
xadmin.site.register(WOTrack, WOTrackAdmin)
xadmin.site.register(WorkOrder, WorkOrderAdmin)