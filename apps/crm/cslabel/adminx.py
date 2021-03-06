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
from apps.crm.services.models import ServicesInfo, ServicesDetail
from apps.crm.customers.models import CustomerInfo


ACTION_CHECKBOX_NAME = '_selected_action'


class RejectSelectedAction(BaseActionView):

    action_name = "reject_selected"
    description = '驳回选中的单据'

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

                if isinstance(obj, LabelOrder):
                    obj.order_status -= 1
                    obj.labeldetial_set.all().delete()
                    obj.process_tag = 5
                    if obj.order_status == 0:
                        self.message_user("%s 取消成功" % obj.order_id, "success")
                    obj.save()

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


# 标签直接创建注册任务
class CreateSTAction(BaseActionView):
    action_name = "create_service_task"
    description = "快捷创建快捷注册任务"
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
                         '%(user)s批量审核了 %(count)d %(items)s.' % {"count": n,
                                                                 "items": model_ngettext(self.opts, n),
                                                                 "user": self.request.user.username})
                queryset.update(order_status=2)
            else:
                for obj in queryset:
                    self.log('change', '%s审核了标签订单' % self.request.user.username, obj)
                    order_detials = obj.labeldetial_set.all()
                    if not order_detials.exists():
                        self.message_user("选择的标签订单不存在客户", "error")
                        obj.mistake_tag = 2
                        obj.save()

                    service_order = ServicesInfo()
                    service_order.prepare_time = datetime.datetime.now()
                    service_order.name = str(obj.order_id) + '标签管理快捷注册任务'
                    service_order.order_category = 2
                    service_order.order_type = 2
                    service_order.quantity = order_detials.count()
                    try:
                        service_order.creator = self.request.user.username
                        service_order.save()
                    except Exception as e:
                        self.message_user("保存任务出错：%s" % e, "error")
                        obj.mistake_tag = 3
                        obj.save()
                        break
                    for order_detial in order_detials:
                        service_detail = ServicesDetail()
                        service_detail.customer = order_detial.customer
                        service_detail.order_type = service_order.order_type
                        service_detail.services = service_order
                        service_detail.target = order_detial.customer.mobile
                        service_detail.creator = self.request.user.username
                        try:
                            service_detail.save()
                        except Exception as e:
                            self.message_user("保存明细出错：%s" % e, "error")
                            obj.mistake_tag = 5
                            obj.save()
                            continue

                    obj.service_num += 1
                    obj.save()
            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')
        return None


# 快捷创建注册任务
class CreateLIAction(BaseActionView):
    action_name = "create_label_task"
    description = "快捷创建快捷注册任务"
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
                         '%(user)s批量审核了 %(count)d %(items)s.' % {"count": n,
                                                                 "items": model_ngettext(self.opts, n),
                                                                 "user": self.request.user.username})
                queryset.update(order_status=2)
            else:
                for obj in queryset:
                    self.log('change', '%s审核了标签订单' % self.request.user.username, obj)
                    order_detials = obj.labelresult_set.all()
                    if not order_detials.exists():
                        self.message_user("选择的标签订单不存在客户", "error")
                        obj.mistake_tag = 2
                        obj.save()

                    service_order = ServicesInfo()
                    serial_number = str(datetime.datetime.now())
                    serial_number = serial_number.replace("-", "").replace(" ", "").replace(":", "").replace(".", "")
                    service_order.prepare_time = datetime.datetime.now()
                    goods_name = str(obj.name).replace('整机：', '').replace(' ', '')
                    service_order.name = str(serial_number) + str(goods_name) + '快捷注册任务'
                    service_order.order_category = 2
                    service_order.order_type = 2
                    service_order.quantity = order_detials.count()
                    try:
                        service_order.creator = self.request.user.username
                        service_order.save()
                    except Exception as e:
                        self.message_user("保存任务出错：%s" % e, "error")
                        obj.mistake_tag = 3
                        obj.save()
                        break
                    for order_detial in order_detials:
                        service_detail = ServicesDetail()
                        service_detail.customer = order_detial.customer
                        service_detail.order_type = service_order.order_type
                        service_detail.services = service_order
                        service_detail.target = order_detial.customer.mobile
                        service_detail.creator = self.request.user.username
                        try:
                            service_detail.save()
                        except Exception as e:
                            self.message_user("保存明细出错：%s" % e, "error")
                            obj.mistake_tag = 5
                            obj.save()
                            continue
            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')
        return None


# 标签明细创建快捷任务
class CreateLDAction(BaseActionView):
    action_name = "create_service_order"
    description = "创建常规客户关系任务"
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
                service_order = ServicesInfo()
                serial_number = str(datetime.datetime.now())
                serial_number = serial_number.replace("-", "").replace(" ", "").replace(":", "").replace(".", "")
                service_order.name = str(serial_number) + '完整标签明细创建任务-需要改名'
                service_order.prepare_time = datetime.datetime.now()
                service_order.order_type = 1
                service_order.quantity = n
                service_order.memorandum = '%s 在订单层创建了客户关系任务' % self.request.user.username
                try:
                    service_order.creator = self.request.user.username
                    service_order.save()
                except Exception as e:
                    self.message_user("创建任务订单保存出错：%s" % e, "error")
                    return None
                customer_list = []
                for obj in queryset:

                    self.log('change', '%s创建了客户关系任务' % self.request.user.username, obj)
                    _q_customer = CustomerInfo.objects.filter(mobile=obj.receiver_mobile)
                    if _q_customer.exists():
                        customer_list.append(_q_customer[0])
                    else:
                        n -= 1
                        continue
                customer_list = set(customer_list)
                n = len(customer_list)
                service_order.quantity = n
                service_order.save()
                for customer in customer_list:
                    service_detail = ServicesDetail()
                    service_detail.customer = customer
                    service_detail.services = service_order
                    service_detail.target = customer.mobile
                    try:
                        service_detail.creator = self.request.user.username
                        service_detail.save()
                    except Exception as e:
                        self.message_user("创建任务订单保存出错：%s" % e, "error")
                        continue

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')
        return None


# 标签界面
class LabelInfoAdmin(object):
    list_display = ['name', 'order_category', 'memorandum', 'order_status', 'creator', 'create_time',]

    actions = [CreateLIAction]

    list_filter = ['name', 'order_category', 'memorandum', 'creator', 'create_time']

    form_layout = [
        Fieldset('基本信息',
                 Row('name', 'order_category',),
                 'memorandum',
                 Row('creator', 'create_time', ),),
        Fieldset(None,
                 'update_time', 'is_delete', **{"style": "display:None"}),
    ]
    relfield_style = 'fk-ajax'


# 标签订单审核界面
class AssociateLabelAdmin(object):
    list_display = ['order_id', 'mistake_tag', 'label', 'quantity', 'order_status', 'creator', 'create_time',]
    readonley_fields = ['order_id', 'label', 'quantity', 'order_status', 'creator',
                        'is_delete', 'create_time', 'update_time']

    actions = [FinishALAction, SubmitALAction, RejectSelectedAction]

    list_filter = ['mistake_tag', 'order_id', 'label',  'creator', 'create_time']

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
    list_display = ['order_id', 'label', 'quantity', 'order_status', 'creator', 'create_time', 'service_num']
    readonley_fields = ['order_id', 'label', 'quantity', 'order_status', 'creator',
                        'is_delete', 'create_time', 'update_time']

    actions = [CreateSTAction]

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
    list_display = ['label_order', 'mistake_tag', 'customer', 'order_status', 'creator', 'create_time', ]
    readonley_fields = ['mistake_tag', 'label_order', 'order_status', 'creator', 'create_time', 'customer',
                        'is_delete', 'update_time']

    actions = [SetALDAction]

    list_filter = ['mistake_tag', 'label_order__order_id', 'customer__mobile', 'creator', 'create_time']

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

    actions = [CreateLDAction]

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

