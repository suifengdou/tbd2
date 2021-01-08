# -*- coding: utf-8 -*-
# @Time    : 2020/11/21 10:58
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

from .models import CustomerInfo, CountIdList, OrderList
from apps.crm.services.models import ServicesInfo, ServicesDetail
from apps.crm.cslabel.models import LabelOrder, LabelDetial


# 订单批量自动标记客户
class SignCusAction(BaseActionView):
    action_name = "sign_customers"
    description = "标记选中的客户"
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

                label_order = LabelOrder()
                serial_number = str(datetime.datetime.now())
                serial_number = serial_number.replace("-", "").replace(" ", "").replace(":", "").replace(".", "")
                label_order.order_id = str(serial_number) + '自定义名称'

                label_order.quantity = n
                try:
                    label_order.creator = self.request.user.username
                    label_order.save()
                except Exception as e:
                    self.message_user("标签单据%s保存出错：%s" % (label_order.order_id, e), "error")
                    return None
                for obj in queryset:
                    label_detial = LabelDetial()
                    label_detial.customer = obj
                    label_detial.label_order = label_order
                    try:
                        label_detial.creator = self.request.user.username
                        label_detial.save()
                    except Exception as e:
                        self.message_user("标签单据明细%s保存出错：%s" % (label_detial.id, e), "error")
                        continue
            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')
        return None


# 快捷创建注册任务
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
                service_order = ServicesInfo()
                serial_number = str(datetime.datetime.now())
                serial_number = serial_number.replace("-", "").replace(" ", "").replace(":", "").replace(".", "")
                service_order.prepare_time = datetime.datetime.now()
                service_order.name = str(serial_number) + '档案创建快捷任务-需要改名'
                service_order.order_category = 2
                service_order.order_type = 2
                service_order.quantity = n
                try:
                    service_order.creator = self.request.user.username
                    service_order.save()
                except Exception as e:
                    self.message_user("保存任务出错：%s" % e, "error")
                    return None

                for obj in queryset:
                    self.log('change', '%s创建了关系任务' % self.request.user.username, obj)

                    service_detail = ServicesDetail()
                    service_detail.customer = obj
                    service_detail.order_type = service_order.order_type
                    service_detail.services = service_order
                    service_detail.target = obj.mobile
                    service_detail.creator = self.request.user.username
                    try:
                        service_detail.save()
                    except Exception as e:
                        self.message_user("保存明细出错：%s" % e, "error")
                        continue
            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')
        return None


class CustomerInfoAdmin(object):
    list_display = ['mobile', 'e_mail', 'qq', 'wangwang', 'jdfbp_id', 'jdzy_id', 'gfsc_id', 'alipay_id', 'pdd_id',
                    'webchat', 'others_id', 'birthday', 'total_amount', 'total_times', 'last_time', 'return_time',
                    'contact_times', 'free_service_times', 'maintenance_times', 'memorandum', 'order_failure_times',
                    'creator', 'create_time']
    readonly_fields = ['mobile', 'e_mail', 'qq', 'wangwang', 'jdfbp_id', 'jdzy_id', 'gfsc_id', 'alipay_id', 'pdd_id',
                       'webchat', 'others_id', 'birthday', 'total_amount', 'total_times', 'last_time', 'return_time',
                       'contact_times', 'free_service_times', 'maintenance_times', 'memorandum', 'order_failure_times',
                       'creator', 'create_time', 'update_time', 'is_delete']
    actions = [CreateSTAction, SignCusAction]

    list_filter = ['mobile', 'wangwang', 'jdfbp_id', 'jdzy_id', 'gfsc_id', 'webchat']
    relfield_style = 'fk-ajax'
    form_layout = [
        Fieldset('基本信息',
                 Row('mobile',),),
        Fieldset('ID信息',
                 Row('wangwang', 'jdfbp_id', 'jdzy_id', ),

                 Row('gfsc_id', 'alipay_id', 'pdd_id', ),
                 Row('webchat', 'others_id',),),
        Fieldset('计数信息',
                 Row('total_amount', 'total_times',),
                 Row('free_service_times', 'maintenance_times',),
                 Row('order_failure_times',),),
        Fieldset(None,
                 'creator', 'create_time', 'update_time', 'is_delete', **{"style": "display:None"}),
    ]

    batch_data = True
    mobile_ids = []

    def post(self, request, *args, **kwargs):
        ids = request.POST.get('ids', None)
        if ids is not None:
            if " " in ids:
                ids = ids.split(" ")
                self.mobile_ids = []
                self.mobile_ids = ids
                self.queryset()
            else:
                self.mobile_ids = []
                self.mobile_ids.append(str(ids).replace("/t", "").replace("/n", "").replace(" ", ""))
                self.queryset()

        return super(CustomerInfoAdmin, self).post(request, *args, **kwargs)

    def queryset(self):
        queryset = super(CustomerInfoAdmin, self).queryset()

        if self.mobile_ids:
            queryset = super(CustomerInfoAdmin, self).queryset().filter(is_delete=0, mobile__in=self.mobile_ids)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


class CountIdListAdmin(object):
    list_display = ['ori_order_trade_no']
    readonly_fields = ['ori_order_trade_no', 'creator', 'create_time', 'update_time', 'is_delete']
    list_filter = ['ori_order_trade_no', 'creator', 'create_time']


class OrderListAdmin(object):
    readonly_fields = ['order', 'creator', 'create_time', 'update_time', 'is_delete']
    list_filter = ['order__trade_no', 'creator', 'create_time']


xadmin.site.register(CustomerInfo, CustomerInfoAdmin)
xadmin.site.register(CountIdList, CountIdListAdmin)
xadmin.site.register(OrderList, OrderListAdmin)

