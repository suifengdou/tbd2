# -*- coding: utf-8 -*-
# @Time    : 2020/11/22 15:11
# @Author  : Hann
# @Site    : 
# @File    : adminx.py
# @Software: PyCharm

import math, re
import datetime
import pandas as pd
import emoji
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.db import router
from django.utils.encoding import force_text
from django.template.response import TemplateResponse
from django.db.models import Sum, Avg, Min, Max, F

from django.contrib.admin.utils import get_deleted_objects

from django.core.files.uploadedfile import InMemoryUploadedFile

import xadmin
from xadmin.plugins.actions import BaseActionView
from xadmin.views.base import filter_hook
from xadmin.util import model_ngettext
from xadmin.layout import Fieldset, Main, Row, Side

from .models import LabelInfo, AssociateLabel, LabelOrder, LabelDetial, LabelResult, AssociateLabelDetial




# 审核标签订单
class SubmitALAction(BaseActionView):
    action_name = "submit_label_order"
    description = "提交选中的单据"
    model_perm = 'change'
    icon = "fa fa-flag"

    modify_models_batch = False

    @filter_hook
    def do_action(self, queryset):
        n = queryset.count()
        if not self.has_change_permission():
            raise PermissionDenied
        if n:
            if self.modify_models_batch:
                self.log('change',
                         '批量审核了 %(count)d %(items)s.' % {"count": n, "items": model_ngettext(self.opts, n)})
                queryset.update(order_status=3)
            else:
                for obj in queryset:
                    self.log('change', '%s审核了标签订单' % self.request.user.username, obj)
                    order_detials = obj.labeldetial_set.all().filter(order_status=1)
                    mistake = 0
                    for detial in order_detials:
                        result_order = LabelResult()
                        result_order.label_order = obj
                        result_order.label = obj.label
                        result_order.customer = detial.customer
                        result_order.creator = self.request.user.username
                        try:
                            result_order.save()
                            detial.order_status = 2
                            detial.save()
                        except Exception as e:
                            self.message_user("%s单据保存出错: %s" % (detial.customer, e), "error")
                            detial.mistake_tag = 1
                            detial.save()
                            mistake = 1
                            continue
                    if mistake:
                        n -= 1
                        obj.mistake_tag = 1
                        obj.save()
                    else:
                        obj.mistake_tag = 0
                        obj.order_status = 2
                        obj.save()
            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')
        return None


# 结束标签订单
class FinishALAction(BaseActionView):
    action_name = "finish_label_order"
    description = "结束选中的单据"
    model_perm = 'change'
    icon = "fa fa-flag"

    modify_models_batch = False

    @filter_hook
    def do_action(self, queryset):
        n = queryset.count()
        if not self.has_change_permission():
            raise PermissionDenied
        if n:
            if self.modify_models_batch:
                self.log('change',
                         '批量审核了 %(count)d %(items)s.' % {"count": n, "items": model_ngettext(self.opts, n)})
                queryset.update(order_status=3)
            else:
                for obj in queryset:
                    self.log('change', '%s审核了标签订单' % self.request.user.username, obj)
                    order_detials = obj.labeldetial_set.all().filter(order_status=1)
                    if not order_detials:
                        obj.mistake_tag = 0
                        obj.order_status = 2
                        obj.save()
                    else:
                        self.message_user("单据还存在未处理的明细单", "error")
            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')
        return None


# 设置完成明细单
class SetALDAction(BaseActionView):
    action_name = "set_label_order_detail"
    description = "设置完成选中的单据"
    model_perm = 'change'
    icon = "fa fa-flag"

    modify_models_batch = True

    @filter_hook
    def do_action(self, queryset):
        n = queryset.count()
        if not self.has_change_permission():
            raise PermissionDenied
        if n:
            if self.modify_models_batch:
                self.log('change',
                         '%(user)s批量审核了 %(count)d %(items)s.' % {"count": n,
                                                                    "items": model_ngettext(self.opts, n),
                                                                    "user": self.request.user.username})
                queryset.update(order_status=2)
            else:
                for obj in queryset:
                    self.log('change', '%s审核了标签订单' % self.request.user.username, obj)
                    order_detials = obj.labeldetial_set.all().filter(order_status=1)
                    if not order_detials:
                        obj.mistake_tag = 0
                        obj.order_status = 2
                        obj.save()
                    else:
                        self.message_user("单据还存在未处理的明细单,先处理明细单", "error")
            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')
        return None


# 创建任务界面
class CreateSTAction(BaseActionView):
    action_name = "create_service_task"
    description = "创建客户关系任务"
    model_perm = 'change'
    icon = "fa fa-flag"

    modify_models_batch = True

    @filter_hook
    def do_action(self, queryset):
        n = queryset.count()
        if not self.has_change_permission():
            raise PermissionDenied
        if n:
            if self.modify_models_batch:
                self.log('change',
                         '%(user)s批量审核了 %(count)d %(items)s.' % {"count": n,
                                                                 "items": model_ngettext(self.opts, n),
                                                                 "user": self.request.user.username})
                queryset.update(order_status=2)
            else:
                for obj in queryset:
                    self.log('change', '%s审核了标签订单' % self.request.user.username, obj)
                    order_detials = obj.labeldetial_set.all().filter(order_status=1)
                    if not order_detials:
                        obj.mistake_tag = 0
                        obj.order_status = 2
                        obj.save()
                    else:
                        self.message_user("单据还存在未处理的明细单,先处理明细单", "error")
            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')
        return None


# 标签创建界面
class LabelInfoAdmin(object):
    list_display = ['name', 'order_category', 'memorandum', 'order_status', 'creator', 'create_time',]

    actions = []

    list_filter = ['name', 'order_category', 'memorandum', 'creator', 'create_time']

    form_layout = [
        Fieldset('基本信息',
                 Row('name', 'order_category',),
                 'memorandum',
                 Row('creator', 'create_time', ),),
        Fieldset(None,
                 'update_time', 'is_delete', **{"style": "display:None"}),
    ]


# 标签订单审核界面
class AssociateLabelAdmin(object):
    list_display = ['order_id', 'label', 'quantity', 'order_status', 'creator', 'create_time',]
    readonley_fields = ['order_id', 'label', 'quantity', 'order_status', 'creator',
                        'is_delete', 'create_time', 'update_time']

    actions = [FinishALAction, SubmitALAction]

    list_filter = ['order_id', 'label',  'creator', 'create_time']

    form_layout = [
        Fieldset('基本信息',
                 Row('order_id', 'label',),
                 'quantity',
                 Row('creator', 'create_time', ),),
        Fieldset(None,
                 'update_time', 'is_delete', **{"style": "display:None"}),
    ]

    def queryset(self):
        queryset = super(AssociateLabelAdmin, self).queryset().filter(order_status=1, is_delete=0)
        return queryset


# 标签查询和任务创建界面
class LabelOrderAdmin(object):
    list_display = ['order_id', 'label', 'quantity', 'order_status', 'creator', 'create_time',]
    readonley_fields = ['order_id', 'label', 'quantity', 'order_status', 'creator',
                        'is_delete', 'create_time', 'update_time']

    actions = []

    list_filter = ['order_id', 'label',  'creator', 'create_time']

    form_layout = [
        Fieldset('基本信息',
                 Row('order_id', 'label',),
                 'quantity',
                 Row('creator', 'create_time', ),),
        Fieldset(None,
                 'update_time', 'is_delete', **{"style": "display:None"}),
    ]


# 标签订单明细未审核界面
class AssociateLabelDetialAdmin(object):
    list_display = ['mistake_tag', 'label_order', 'customer', 'order_status', 'creator', 'create_time', ]
    readonley_fields = ['mistake_tag', 'label_order', 'order_status', 'creator', 'create_time', 'customer',
                        'is_delete', 'update_time']

    actions = [SetALDAction]

    list_filter = ['label_order__order_id', 'customer__mobile', 'creator', 'create_time']

    form_layout = [
        Fieldset('基本信息',
                 Row('customer', 'label', ),
                 Row('creator', 'create_time', ), ),
        Fieldset(None,
                 'update_time', 'is_delete', **{"style": "display:None"}),
    ]

    def queryset(self):
        queryset = super(AssociateLabelDetialAdmin, self).queryset().filter(order_status=1, is_delete=0)
        return queryset


# 标签订单明细查询界面
class LabelDetialAdmin(object):
    list_display = ['mistake_tag', 'label_order', 'customer', 'order_status', 'creator', 'create_time', ]
    readonley_fields = ['mistake_tag', 'label_order', 'order_status', 'creator', 'create_time', 'customer',
                        'is_delete', 'update_time']

    actions = []

    list_filter = ['label_order__order_id', 'customer__mobile', 'creator', 'create_time']

    form_layout = [
        Fieldset('基本信息',
                 Row('customer', 'label', ),
                 Row('creator', 'create_time', ), ),
        Fieldset(None,
                 'update_time', 'is_delete', **{"style": "display:None"}),
    ]


# 完整标签查询界面
class LabelResultAdmin(object):
    list_display = ['mistake_tag', 'label_order', 'label', 'customer', 'order_status', 'creator', 'create_time', ]
    readonley_fields = ['mistake_tag', 'label_order', 'label', 'order_status', 'creator', 'create_time', 'customer',
                        'is_delete', 'update_time']

    actions = []

    list_filter = ['label__name', 'customer__mobile', 'creator', 'create_time']

    form_layout = [
        Fieldset('基本信息',
                 Row('customer', 'label', ),
                 Row('creator', 'create_time', ), ),
        Fieldset(None,
                 'update_time', 'is_delete', **{"style": "display:None"}),
    ]


xadmin.site.register(LabelInfo, LabelInfoAdmin)
xadmin.site.register(AssociateLabel, AssociateLabelAdmin)
xadmin.site.register(LabelOrder, LabelOrderAdmin)
xadmin.site.register(AssociateLabelDetial, AssociateLabelDetialAdmin)
xadmin.site.register(LabelDetial, LabelDetialAdmin)
xadmin.site.register(LabelResult, LabelResultAdmin)

