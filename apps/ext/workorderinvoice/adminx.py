# -*- coding: utf-8 -*-
# @Time    : 2020/3/23 16:34
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

import math, re
import datetime
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.db import router
from django.utils.encoding import force_text
from django.template.response import TemplateResponse
from django.db.models import Sum, Avg, Min, Max, F
from django.db import models

from django.contrib.admin.utils import get_deleted_objects

import pandas as pd
import xadmin
from xadmin.plugins.actions import BaseActionView
from xadmin.views.base import filter_hook
from xadmin.util import model_ngettext
from xadmin.layout import Fieldset


from .models import WorkOrder, GoodsDetail, InvoiceOrder, InvoiceGoods, WOUnhandle, WOCheck, IOhandle, IOCheck
from apps.utils.geography.models import DistrictInfo


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
                if obj.order_status > 0:
                    obj.order_status -= 1
                    obj.save()
                    if obj.order_status == 0:
                        self.message_user("%s 取消成功" % obj.order_id, "success")
                    else:
                        self.message_user("%s 驳回上一级成功" % obj.order_id, "success")
                else:
                    n -= 1
                    self.message_user("%s 单据状态错误，请检查，驳回出错。" % obj.order_id, "error")
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
class SubmitWOAction(BaseActionView):
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
                    # 字符串字段去特殊字符
                    check_fields = ['order_id', 'invoice_id', 'title', 'tax_id', 'phone', 'bank', 'account',
                                    'sent_consignee', 'sent_smartphone', 'sent_district', 'sent_address']
                    for key in check_fields:
                        value = getattr(obj, key, None)
                        if value:
                            setattr(obj, key, str(value).replace(' ', '').replace("'", '').replace('\n', ''))

                    if not obj.company:
                        self.message_user("%s 没开票公司" % obj.order_id, "error")
                        obj.mistake_tag = 1
                        obj.save()
                        n -= 1
                        continue

                    if obj.amount <= 0:
                        self.message_user("%s 没添加货品, 或者货品价格添加错误" % obj.order_id, "error")
                        obj.mistake_tag = 2
                        obj.save()
                        n -= 1
                        continue
                    # 判断专票信息是否完整
                    if obj.order_category == 1:
                        if any([obj.phone, obj.bank, obj.account, obj.address]):
                            self.message_user("%s 专票信息缺" % obj.order_id, "error")
                            obj.mistake_tag = 3
                            obj.save()
                            n -= 1
                            continue
                    if obj.is_deliver == 1:
                        if not re.match(r'^[0-9]+$', obj.sent_smartphone):
                            self.message_user("%s 收件人手机错误" % obj.order_id, "error")
                            obj.mistake_tag = 4
                            obj.save()
                            n -= 1
                            continue

                    obj.order_status = 2
                    obj.mistake_tag = 0

                    obj.save()
                    self.message_user("%s 审核完毕，等待客户反馈" % obj.order_id, "info")

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


# 审核不用拆单工单
class CheckWOAction(BaseActionView):
    action_name = "submit_single_wo"
    description = "提交未超限工单"
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
                    if obj.order_category == 1:
                        if obj.amount > obj.company.special_invoice:
                            self.message_user("%s 需要拆单的发票，用拆单递交" % obj.order_id, "error")
                            obj.mistake_tag = 5
                            obj.save()
                            n -= 1
                            continue
                    else:
                        if obj.amount > obj.company.spain_invoice:
                            self.message_user("%s 超限额的发票，用拆单递交" % obj.order_id, "error")
                            obj.mistake_tag = 5
                            obj.save()
                            n -= 1
                            continue

                    invoice_order = IOhandle()
                    copy_fields_order = ['shop', 'company', 'order_id', 'order_category', 'title', 'tax_id', 'phone', 'bank',
                                   'account', 'address', 'remark', 'sent_consignee', 'sent_smartphone', 'sent_city',
                                   'sent_district', 'sent_address', 'amount', 'is_deliver', 'message']
                    for key in copy_fields_order:
                        value = getattr(obj, key, None)
                        setattr(invoice_order, key, value)

                    invoice_order.sent_province = obj.sent_city.province
                    invoice_order.creator = self.request.user.username
                    invoice_order.ori_amount = obj.amount
                    try:
                        invoice_order.save()
                    except Exception as e:
                        self.message_user("%s 递交发票出错 %s" % (obj.order_id, e), "error")
                        obj.mistake_tag = 6
                        obj.save()
                        n -= 1
                        continue
                    _q_goods = obj.goodsdetail_set.all()
                    for good in _q_goods:
                        invoice_good = InvoiceGoods()
                        invoice_good.invoice = invoice_order
                        copy_fields_goods = ['goods_id', 'goods_name', 'quantity', 'price', 'memorandum']
                        for key in copy_fields_goods:
                            value = getattr(good, key, None)
                            setattr(invoice_good, key, value)
                        try:
                            invoice_good.creator = self.request.user.username
                            invoice_good.save()
                        except Exception as e:
                            self.message_user("%s 生成发票货品出错 %s" % (obj.order_id, e), "error")
                            obj.mistake_tag = 7
                            obj.save()
                            continue

                    obj.order_status = 3
                    obj.mistake_tag = 0

                    obj.save()
                    self.message_user("%s 审核完毕，等待客户反馈" % obj.order_id, "info")

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


# 审核拆单工单
class SplitWOAction(BaseActionView):
    action_name = "submit_split_wo"
    description = "提交超限额工单"
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
                    quota = 0
                    if obj.order_category == 1:
                        if obj.amount > obj.company.special_invoice:
                            quota = obj.company.special_invoice
                            obj.mistake_tag = 5
                    else:
                        if obj.amount > obj.company.spain_invoice:
                            quota = obj.company.spain_invoice
                            obj.mistake_tag = 5

                    if obj.mistake_tag == 5:
                        _q_goods = obj.goodsdetail_set.all()

                        l_name, l_quantity, l_price = [goods.goods_id for goods in _q_goods], [goods.quantity for goods in _q_goods], [goods.price for goods in _q_goods]
                        print(l_name, l_quantity, l_price)
                        if max(l_price) > quota:
                            self.message_user("%s 此订单为无法拆单的超限额工单，需驳回修正" % obj.order_id, "error")
                            obj.mistake_tag = 8
                            obj.save()
                            n -= 1
                            continue
                        amounts = list(map(lambda x, y: x * y, l_quantity, l_price))
                        total_amount = 0
                        for i in amounts:
                            total_amount = total_amount + i

                        _rt_name = []
                        _rt_quantity = []

                        parts = math.ceil(total_amount / quota)
                        part_amount = math.ceil(total_amount / parts) + 1
                        if part_amount < max(l_price):
                            part_amount = max(l_price)
                        groups = []

                        current_quantity = list(l_quantity)

                        while True:
                            if _rt_quantity == l_quantity:
                                break
                            group = {}
                            group_amount = 0
                            end_tag = 0
                            for i in range(len(l_name)):
                                if end_tag:
                                    break
                                amount = current_quantity[i] * l_price[i]
                                if amount == 0:
                                    continue
                                if (amount + group_amount) < part_amount:
                                    group[l_name[i]] = [current_quantity[i], l_price[i]]

                                    if l_name[i] in _rt_name:
                                        goods_num = l_name.index(l_name[i])
                                        _rt_quantity[goods_num] = _rt_quantity[goods_num] + current_quantity[i]
                                    else:
                                        _rt_name.append(l_name[i])
                                        _rt_quantity.append(current_quantity[i])
                                    current_quantity[i] = 0
                                    if group:
                                        group_amount = 0
                                        for k, v in group.items():
                                            group_amount = group_amount + v[0] * v[1]
                                    if current_quantity[-1] == 0:
                                        groups.append(group)
                                        break
                                else:
                                    for step in range(1, current_quantity[i] + 1):
                                        if (current_quantity[i] - step) == 0:
                                            groups.append(group)
                                            end_tag = 1
                                            break
                                        increment = current_quantity[i] - step
                                        amount = increment * l_price[i]
                                        if (amount + group_amount) < part_amount:
                                            group[l_name[i]] = [increment, l_price[i]]

                                            if l_name[i] in _rt_name:
                                                goods_num = l_name.index(l_name[i])
                                                _rt_quantity[goods_num] = _rt_quantity[goods_num] + increment
                                                current_quantity[i] = current_quantity[i] - increment
                                            else:
                                                _rt_name.append(l_name[i])
                                                _rt_quantity.append(increment)
                                                current_quantity[i] = current_quantity[i] - increment
                                            groups.append(group)
                                            end_tag = 1
                                            break





                        invoice_order = IOhandle()
                        copy_fields_order = ['shop', 'company', 'order_id', 'order_category', 'title', 'tax_id', 'phone', 'bank',
                                       'account', 'address', 'remark', 'sent_consignee', 'sent_smartphone', 'sent_city',
                                       'sent_district', 'sent_address', 'amount', 'is_deliver', 'message']
                        for key in copy_fields_order:
                            value = getattr(obj, key, None)
                            setattr(invoice_order, key, value)

                        invoice_order.sent_province = obj.sent_city.province
                        invoice_order.creator = self.request.user.username
                        invoice_order.ori_amount = obj.amount
                        try:
                            invoice_order.save()
                        except Exception as e:
                            self.message_user("%s 递交发票出错 %s" % (obj.order_id, e), "error")
                            obj.mistake_tag = 6
                            obj.save()
                            n -= 1
                            continue
                    _q_goods = obj.goodsdetail_set.all()
                    for good in _q_goods:
                        invoice_good = InvoiceGoods()
                        invoice_good.invoice = invoice_order
                        copy_fields_goods = ['goods_id', 'goods_name', 'quantity', 'price', 'memorandum']
                        for key in copy_fields_goods:
                            value = getattr(good, key, None)
                            setattr(invoice_good, key, value)
                        try:
                            invoice_good.creator = self.request.user.username
                            invoice_good.save()
                        except Exception as e:
                            self.message_user("%s 生成发票货品出错 %s" % (obj.order_id, e), "error")
                            obj.mistake_tag = 7
                            obj.save()
                            continue

                    obj.order_status = 3
                    obj.mistake_tag = 0

                    obj.save()
                    self.message_user("%s 审核完毕，等待客户反馈" % obj.order_id, "info")

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


class GoodsDetailInline(object):
    model = GoodsDetail
    exclude = ['creator', 'goods_id', 'is_delete', 'order_id']

    extra = 1
    style = 'table'


# 发票工单创建界面
class WOUnhandleAdmin(object):
    list_display = ['company', 'order_id', 'process_tag', 'mistake_tag', 'memorandum', 'order_status', 'message',
                    'order_category', 'title', 'tax_id', 'phone', 'bank', 'account', 'address', 'remark', 'is_deliver',
                    'sent_consignee', 'sent_smartphone', 'sent_city', 'sent_district', 'sent_address', 'amount']
    actions = [SubmitWOAction, RejectSelectedAction, ]

    search_fields = []
    list_filter = []

    list_editable = ['order_category', 'title', 'tax_id', 'phone', 'bank', 'account', 'address', 'remark',
                     'sent_consignee', 'sent_smartphone', 'sent_city', 'sent_district', 'sent_address', 'is_deliver',
                     'message', 'is_deliver']
    readonly_fields = []
    inlines = [GoodsDetailInline]

    form_layout = [
        Fieldset('收款开票公司信息',
                 'shop', 'company', 'order_id', 'order_category', ),
        Fieldset('发票信息',
                 'title', 'tax_id', 'phone', 'bank', 'account', 'address', 'remark'),
        Fieldset('发货快递相关信息',
                 'is_deliver', 'sent_consignee', 'sent_smartphone', 'sent_city', 'sent_district', 'sent_address'),
        Fieldset(None,
                 'amount', 'submit_time', 'handle_time', 'handle_interval', 'memorandum', 'process_tag',
                 'mistake_tag', 'order_status', 'is_delete', 'creator',
                 **{"style": "display:None"}),
    ]

    def save_models(self):
        obj = self.new_obj
        request = self.request
        obj.creator = request.user.username
        if obj.shop.company:
            obj.company = obj.shop.company
        obj.save()
        super().save_models()

    def save_related(self):
        for i in range(self.formsets[0].forms.__len__()):
            try:
                if self.formsets[0].forms[i].instance.quantity > 0:
                    request = self.request
                    self.formsets[0].forms[i].instance.goods_id = self.formsets[0].forms[i].instance.goods_name.goods_id
                    self.formsets[0].forms[i].instance.creator = request.user.username
            except Exception as e:
                self.message_user("%s 添加的货品不能为空，此单未保存货品" % e, "info")
                self.queryset()
                break
        super().save_related()

    def queryset(self):
        queryset = super(WOUnhandleAdmin, self).queryset()
        if self.request.user.is_superuser == 1:
            queryset = queryset.filter(order_status=1, is_delete=0)
        else:
            queryset = queryset.filter(order_status=1, is_delete=0, creator=self.request.user.username)
        for obj in queryset:
            try:
                amount = obj.goodsdetail_set.all().aggregate(
                    sum_product=Sum(F("quantity") * F('price'), output_field=models.FloatField()))["sum_product"]
            except Exception as e:
                amount = 0
                print(e)
            if amount is None:
                amount = 0
            obj.amount = amount
            obj.save()
        return queryset


# 财务审核工单界面
class WOCheckAdmin(object):
    list_display = ['company', 'order_id', 'process_tag', 'mistake_tag', 'memorandum', 'order_status', 'order_category', 'title',
                    'tax_id', 'phone', 'bank', 'account', 'address', 'remark', 'sent_consignee', 'sent_smartphone',
                    'sent_city', 'sent_district', 'sent_address', 'amount', 'is_deliver', 'message',
                    ]

    actions = [CheckWOAction, SplitWOAction, RejectSelectedAction]
    inlines = [GoodsDetailInline]

    search_fields = []
    list_filter = []
    list_editable = ['memorandum',]
    readonly_fields = ['shop', 'company', 'order_id', 'order_category', 'title', 'tax_id', 'phone', 'bank', 'account',
                       'address', 'remark', 'sent_consignee', 'sent_smartphone', 'sent_city',
                       'sent_district', 'sent_address', 'amount', 'is_deliver', 'submit_time', 'handle_time',
                       'handle_interval', 'message', 'process_tag', 'mistake_tag', 'order_status']

    form_layout = [
        Fieldset('收款开票公司信息',
                 'shop', 'company', 'order_id', 'order_category', ),
        Fieldset('发票信息',
                 'title', 'tax_id', 'phone', 'bank', 'account', 'address', 'remark'),
        Fieldset('发货快递相关信息',
                 'is_deliver', 'sent_consignee', 'sent_smartphone', 'sent_city', 'sent_district', 'sent_address'),
        Fieldset(None,
                 'amount', 'submit_time', 'handle_time', 'handle_interval', 'memorandum', 'process_tag',
                 'mistake_tag', 'order_status', 'is_delete', 'creator',
                 **{"style": "display:None"}),
    ]

    def queryset(self):
        queryset = super(WOCheckAdmin, self).queryset()
        queryset = queryset.filter(order_status=2, is_delete=0)
        return queryset


# 发票工单查询界面
class WorkOrderAdmin(object):
    list_display = ['company', 'order_id', 'process_tag', 'mistake_tag', 'order_status', 'order_category', 'title',
                    'tax_id', 'phone', 'bank', 'account', 'address', 'remark', 'sent_consignee', 'sent_smartphone',
                    'sent_city', 'sent_district', 'sent_address', 'amount', 'is_deliver', 'message',
                    'memorandum']

    actions = [RejectSelectedAction]

    search_fields = []
    list_filter = []
    readonly_fields = []
    inlines = [GoodsDetailInline]

    form_layout = [
        Fieldset('收款开票公司信息',
                 'shop', 'company', 'order_id', 'order_category', ),
        Fieldset('发票信息',
                 'title', 'tax_id', 'phone', 'bank', 'account', 'address', 'remark'),
        Fieldset('发货快递相关信息',
                 'is_deliver', 'sent_consignee', 'sent_smartphone', 'sent_city', 'sent_district', 'sent_address'),
        Fieldset(None,
                 'amount', 'submit_time', 'handle_time', 'handle_interval', 'memorandum', 'process_tag',
                 'mistake_tag', 'order_status', 'is_delete', 'creator',
                 **{"style": "display:None"}),
    ]

    def queryset(self):
        queryset = super(WorkOrderAdmin, self).queryset()
        queryset = queryset.filter(is_delete=0)
        return queryset


# 发票工单货品界面
class GoodsDetailAdmin(object):
    list_display = ['invoice', 'goods_id', 'goods_name', 'quantity', 'creator']


class InvoiceGoodsInline(object):
    model = InvoiceGoods
    exclude = ['creator', 'goods_id', 'is_delete', 'order_id']

    extra = 0
    style = 'table'


# 发票订单处理界面
class IOhandleAdmin(object):
    list_display = ['company', 'order_id', 'process_tag', 'mistake_tag', 'order_status', 'order_category', 'title',
                    'tax_id', 'phone', 'bank', 'account', 'ori_amount', 'address', 'remark', 'sent_consignee', 'sent_smartphone',
                    'sent_province', 'sent_city', 'sent_district', 'sent_address', 'amount', 'is_deliver', 'message',
                    'memorandum']

    search_fields = []
    list_filter = []
    readonly_fields = []
    inlines = [InvoiceGoodsInline]

    form_layout = [
        Fieldset('收款开票公司信息',
                 'shop', 'company', 'order_id', 'order_category', ),
        Fieldset('发票信息',
                 'title', 'tax_id', 'phone', 'bank', 'account', 'address', 'remark'),
        Fieldset('发货快递相关信息',
                 'is_deliver', 'sent_consignee', 'sent_smartphone', 'sent_province', 'sent_city', 'sent_district',
                 'sent_address'),
        Fieldset(None,
                 'amount', 'submit_time', 'handle_time', 'handle_interval', 'memorandum', 'process_tag',
                 'mistake_tag', 'order_status', 'is_delete', 'creator', 'track_no',
                 **{"style": "display:None"}),
    ]

    def queryset(self):
        queryset = super(IOhandleAdmin, self).queryset()
        queryset = queryset.filter(order_status=1, is_delete=0)
        return queryset


# 申请人确认界面
class IOCheckAdmin(object):
    list_display = ['company', 'order_id', 'process_tag', 'mistake_tag', 'order_status', 'order_category', 'title',
                    'tax_id', 'phone', 'bank', 'account', 'ori_amount', 'address', 'remark', 'sent_consignee', 'sent_smartphone',
                    'sent_province', 'sent_city', 'sent_district', 'sent_address', 'amount', 'is_deliver', 'message',
                    'memorandum']

    search_fields = []
    list_filter = []
    readonly_fields = []
    inlines = [InvoiceGoodsInline]

    form_layout = [
        Fieldset('收款开票公司信息',
                 'shop', 'company', 'order_id', 'order_category', ),
        Fieldset('发票信息',
                 'title', 'tax_id', 'phone', 'bank', 'account', 'address', 'remark'),
        Fieldset('发货快递相关信息',
                 'is_deliver', 'sent_consignee', 'sent_smartphone', 'sent_province', 'sent_city', 'sent_district',
                 'sent_address'),
        Fieldset(None,
                 'amount', 'submit_time', 'handle_time', 'handle_interval', 'memorandum', 'process_tag',
                 'mistake_tag', 'order_status', 'is_delete', 'creator', 'track_no',
                 **{"style": "display:None"}),
    ]

    def queryset(self):
        queryset = super(IOCheckAdmin, self).queryset()
        queryset = queryset.filter(order_status=2, is_delete=0)
        return queryset


class InvoiceOrderAdmin(object):
    list_display = ['company', 'order_id', 'process_tag', 'mistake_tag', 'order_status', 'order_category', 'title',
                    'tax_id', 'phone', 'bank', 'account', 'ori_amount', 'address', 'remark', 'sent_consignee', 'sent_smartphone',
                    'sent_province', 'sent_city', 'sent_district', 'sent_address', 'amount', 'is_deliver', 'message',
                    'memorandum']

    search_fields = []
    list_filter = []
    readonly_fields = []
    inlines = [InvoiceGoodsInline]

    form_layout = [
        Fieldset('收款开票公司信息',
                 'shop', 'company', 'order_id', 'order_category', ),
        Fieldset('发票信息',
                 'title', 'tax_id', 'phone', 'bank', 'account', 'address', 'remark'),
        Fieldset('发货快递相关信息',
                 'is_deliver', 'sent_consignee', 'sent_smartphone', 'sent_province', 'sent_city', 'sent_district',
                 'sent_address'),
        Fieldset(None,
                 'amount', 'submit_time', 'handle_time', 'handle_interval', 'memorandum', 'process_tag',
                 'mistake_tag', 'order_status', 'is_delete', 'creator', 'track_no',
                 **{"style": "display:None"}),
    ]


class InvoiceGoodsAdmin(object):
    list_display = ['invoice', 'goods_id', 'goods_name', 'quantity', 'creator']


xadmin.site.register(WOUnhandle, WOUnhandleAdmin)
xadmin.site.register(WOCheck, WOCheckAdmin)
xadmin.site.register(WorkOrder, WorkOrderAdmin)
xadmin.site.register(IOhandle, IOhandleAdmin)
xadmin.site.register(IOCheck, IOCheckAdmin)
xadmin.site.register(InvoiceOrder, InvoiceOrderAdmin)
xadmin.site.register(GoodsDetail, GoodsDetailAdmin)
xadmin.site.register(InvoiceGoods, InvoiceGoodsAdmin)
