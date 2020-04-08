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
from xadmin.layout import Fieldset, Main, Row, Side


from .models import WorkOrder, GoodsDetail, InvoiceOrder, InvoiceGoods, WOUnhandle, WOCheck, IOhandle, IOCheck, DeliverOrder, DOCheck, WOApply
from apps.utils.geography.models import DistrictInfo
from apps.base.goods.models import MachineInfo


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
                if hasattr(obj, 'work_order'):
                    check_tag = False
                else:
                    check_tag = True
                if check_tag:
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
                else:
                    if n > 1:
                        self.message_user("驳回选中数量错误：%s个， 驳回只允许单个订单驳回，" % n, "error")
                        return None
                    for obj in queryset:
                        mistake_tag = 0
                        _q_invoice_orders = obj.work_order.invoiceorder_set.all()
                        for invoice_order in _q_invoice_orders:
                            if invoice_order.order_status == 2:
                                n -= 1
                                self.message_user("%s 请确保此工单所有的发票订单都为未开票状态。" % obj.work_order, "error")
                                mistake_tag = 1
                                continue
                        if mistake_tag:
                            continue
                        else:

                            for invoice_order in _q_invoice_orders:
                                try:
                                    invoice_order.invoicegoods_set.all().delete()
                                except Exception as e:
                                    self.message_user("%s 删除货品信息失败。错误：%s" % (invoice_order, e), "error")
                                    mistake_tag = 1
                                    continue
                            if mistake_tag:
                                self.message_user("%s 此订单驳回出错，需要联系管理员。" % obj.work_order, "error")
                                obj.mistake_tag = 4
                                obj.save()
                                continue

                            obj.work_order.order_status = 2
                            obj.work_order.process_tag = 5
                            obj.work_order.mistake_tag = 12
                            obj.work_order.save()

                            try:
                                _q_invoice_orders.delete()
                            except Exception as e:
                                self.message_user("删除订单失败。错误：%s" % e, "error")
                                obj.mistake_tag = 4
                                obj.save()
                                continue
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
                        if not any([obj.phone, obj.bank, obj.account, obj.address]):
                            self.message_user("%s 专票信息缺" % obj.order_id, "error")
                            obj.mistake_tag = 3
                            obj.save()
                            n -= 1
                            continue
                    if obj.is_deliver == 1:
                        if not re.match(r'^[0-9-]+$', obj.sent_smartphone):
                            self.message_user("%s 收件人手机错误" % obj.order_id, "error")
                            obj.mistake_tag = 4
                            obj.save()
                            n -= 1
                            continue
                    if not re.match("^([159Y]{1})([1239]{1})([0-9ABCDEFGHJKLMNPQRTUWXY]{6})([0-9ABCDEFGHJKLMNPQRTUWXY]{9})([0-90-9ABCDEFGHJKLMNPQRTUWXY])$", obj.tax_id):

                        self.message_user("%s 税号错误" % obj.order_id, "error")
                        obj.mistake_tag = 13
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
                        if int(obj.amount) > int(obj.company.special_invoice):
                            self.message_user("%s 需要拆单的发票，用拆单递交" % obj.order_id, "error")
                            obj.mistake_tag = 5
                            obj.save()
                            n -= 1
                            continue
                    else:
                        if int(obj.amount) > int(obj.company.spain_invoice):
                            self.message_user("%s 超限额的发票，用拆单递交" % obj.order_id, "error")
                            obj.mistake_tag = 5
                            obj.save()
                            n -= 1
                            continue

                    invoice_order = IOhandle()
                    copy_fields_order = ['shop', 'company', 'order_id', 'order_category', 'title', 'tax_id', 'phone', 'bank',
                                   'account', 'address', 'remark', 'sent_consignee', 'sent_smartphone', 'sent_city',
                                   'sent_district', 'sent_address', 'amount', 'is_deliver', 'message', 'creator']
                    for key in copy_fields_order:
                        value = getattr(obj, key, None)
                        setattr(invoice_order, key, value)

                    invoice_order.sent_province = obj.sent_city.province
                    invoice_order.creator = obj.creator
                    invoice_order.ori_amount = obj.amount
                    invoice_order.work_order = obj
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
                    error_tag = 0
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

                        l_name, l_quantity, l_price = [goods.goods_name for goods in _q_goods], [goods.quantity for goods in _q_goods], [goods.price for goods in _q_goods]
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
                        part_amount = quota - 1

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

                        invoice_quantity = len(groups)
                        for invoice_num in range(invoice_quantity):
                            invoice_order = IOhandle()
                            series_number = invoice_num + 1
                            order_id = '%s-%s' % (obj.order_id, series_number)

                            _q_invoice_order = InvoiceOrder.objects.filter(order_id=order_id)
                            if _q_invoice_order.exists():
                                self.message_user("%s 发票工单重复生成发票订单，检查后处理" % obj.order_id, "error")
                                obj.mistake_tag = 9
                                obj.save()
                                n -= 1
                                error_tag = 1
                                continue
                            invoice_order.order_id = order_id

                            invoice_order.work_order = obj
                            copy_fields_order = ['shop', 'company', 'order_category', 'title', 'tax_id', 'phone', 'bank',
                                           'account', 'address', 'remark', 'sent_consignee', 'sent_smartphone', 'sent_city',
                                           'sent_district', 'sent_address',  'is_deliver', 'message', 'creator']
                            for key in copy_fields_order:
                                value = getattr(obj, key, None)
                                setattr(invoice_order, key, value)

                            invoice_order.sent_province = obj.sent_city.province
                            invoice_order.creator = obj.creator
                            invoice_order.ori_amount = obj.amount
                            try:
                                invoice_order.save()
                            except Exception as e:
                                self.message_user("%s 生成发票订单出错，请仔细检查 %s" % (obj.order_id, e), "error")
                                obj.mistake_tag = 10
                                obj.save()
                                error_tag = 1
                                n -= 1
                                continue
                            current_amount = 0
                            for goods, detail in groups[invoice_num].items():
                                goods_order = InvoiceGoods()
                                current_amount = current_amount + (detail[0] * detail[1])
                                goods_order.invoice = invoice_order
                                goods_order.goods_name = goods
                                goods_order.goods_id = goods.goods_id
                                goods_order.quantity = detail[0]
                                goods_order.price = detail[1]
                                goods_order.memorandum = '来源 %s 的第 %s 张发票' % (obj.order_id, invoice_num + 1)

                                try:
                                    goods_order.save()
                                except Exception as e:
                                    self.message_user("%s 生成发票订单货品出错，请仔细检查 %s" % (obj.order_id, e), "error")
                                    obj.mistake_tag = 11
                                    obj.save()
                                    n -= 1
                                    error_tag = 1
                                    continue

                            invoice_order.amount = current_amount
                            invoice_order.save()

                        if error_tag == 1:
                            n -= 1
                            continue

                        obj.order_status = 3
                        obj.save()

                    else:
                        self.message_user("%s 非超额订单，请用未超限额模式审核。" % obj.order_id, "error")
                        obj.mistake_tag = 0
                        obj.save()
                        n -= 1
                        continue

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


# 审核开票完成的发票订单
class SubmitIOAction(BaseActionView):
    action_name = "submit_r_io"
    description = "审核选中的发票"
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
                    if not obj.invoice_id:
                        self.message_user("%s 此单还没有开票" % obj.order_id, "error")
                        obj.mistake_tag = 1
                        obj.save()
                        n -= 1
                        continue
                    _q_work_order = DeliverOrder.objects.filter(work_order=obj.work_order, order_status=1)
                    if _q_work_order.exists():
                        deliver_order = _q_work_order[0]
                        if str(obj.invoice_id) in str(deliver_order.ori_order_id):
                            self.message_user("%s 重复递交了订单" % obj.order_id, "error")
                            obj.order_status = 2
                            obj.mistake_tag = 0
                            obj.save()
                            n -= 1
                            continue
                        else:
                            deliver_order.ori_order_id = '%s,%s' % (deliver_order.ori_order_id, obj.invoice_id)
                            invoice_num = len(deliver_order.ori_order_id.split(','))
                            deliver_order.message = '%s共%s张' % (obj.creator, invoice_num)
                            deliver_order.save()
                            obj.order_status = 2
                            obj.mistake_tag = 0
                            obj.save()
                            continue
                    else:
                        deliver_order = DeliverOrder()
                        deliver_order.work_order = obj.work_order
                        deliver_order.shop = obj.shop.shop_name
                        deliver_order.ori_order_id = obj.invoice_id
                        deliver_order.province = obj.sent_city.province.province
                        deliver_order.city = obj.sent_city.city
                        deliver_order.nickname = obj.sent_consignee
                        deliver_order.consignee = obj.sent_consignee
                        deliver_order.smartphone = obj.sent_smartphone
                        deliver_order.message = '%s共1张' % obj.creator
                        deliver_order.address = obj.sent_address

                        if obj.is_deliver == 1:
                            deliver_order.logistics = '顺丰'
                        else:
                            deliver_order.logistics = '申通'
                        if obj.sent_district:
                            _q_district = DistrictInfo.objects.filter(city=obj.sent_city, district=obj.sent_district)
                            if _q_district.exists():
                                deliver_order.district = _q_district[0].district
                            else:
                                deliver_order.district = '其他区'
                        try:
                            deliver_order.save()
                        except Exception as e:
                            self.message_user("%s 生成快递运单失败，请仔细检查 %s" % (obj.order_id, e), "error")
                            obj.mistake_tag = 2
                            obj.save()
                            n -= 1
                            continue
                    obj.order_status = 2
                    obj.mistake_tag = 0
                    obj.process_tag = 4

                    obj.save()
                    self.message_user("%s 审核完毕，等待客户反馈" % obj.order_id, "info")

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


# 终审发票订单
class CheckIOAction(BaseActionView):
    action_name = "check_r_io"
    description = "审核选中的发票"
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
                    if obj.process_tag != 5:
                        if not obj.invoice_id:
                            self.message_user("%s 此单还没有开票" % obj.order_id, "error")
                            obj.mistake_tag = 1
                            obj.save()
                            n -= 1
                            continue
                        if not obj.track_no:
                            self.message_user("%s 此单还没有打印快递单" % obj.order_id, "error")
                            obj.mistake_tag = 3
                            obj.save()
                            n -= 1
                            continue
                        obj.process_tag = 5
                    obj.order_status = 3
                    obj.mistake_tag = 0
                    obj.save()
                    self.message_user("%s 审核完毕，等待客户反馈" % obj.order_id, "info")

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


# 审核打单完毕的发货单
class SubmitDOAction(BaseActionView):
    action_name = "submit_r_do"
    description = "审核选中的发货单"
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
                    if obj.process_tag == 0:
                        if not obj.track_no:
                            self.message_user("%s 此单还没有打印，不能递交" % obj.ori_order_id, "error")
                            obj.mistake_tag = 1
                            obj.save()
                            n -= 1
                            continue
                        else:
                            obj.process_tag = 1
                    _q_invoice_orders = obj.work_order.invoiceorder_set.all()
                    if _q_invoice_orders.exists():
                        for invoice_order in _q_invoice_orders:
                            if invoice_order.invoice_id not in obj.ori_order_id:
                                continue
                            invoice_order.track_no = '%s：%s' % (obj.logistics, obj.track_no)
                            try:
                                invoice_order.process_tag = 5
                                invoice_order.save()
                            except Exception as e:
                                self.message_user("%s 回写快递单号失败，请仔细检查 %s" % (obj.ori_order_id, e), "error")
                                obj.mistake_tag = 2
                                obj.save()
                                n -= 1
                                continue

                    obj.order_status = 2
                    obj.mistake_tag = 0

                    obj.save()

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


class GoodsDetailInline(object):
    model = GoodsDetail
    exclude = ['creator', 'goods_id', 'is_delete', 'order_id']

    extra = 1
    style = 'table'


# 发票工单创建界面
class WOApplyAdmin(object):
    list_display = ['company', 'order_id', 'process_tag', 'mistake_tag', 'memorandum', 'order_status', 'message',
                    'order_category', 'title', 'tax_id', 'phone', 'bank', 'account', 'address', 'remark', 'is_deliver',
                    'sent_consignee', 'sent_smartphone', 'sent_city', 'sent_district', 'sent_address', 'amount']
    actions = [SubmitWOAction, RejectSelectedAction, ]

    search_fields = ['order_id']
    list_filter = ['company__company_name', 'process_tag', 'mistake_tag', 'order_category', 'title', 'tax_id', 'amount']

    list_editable = ['order_category', 'title', 'tax_id', 'phone', 'bank', 'account', 'address', 'remark',
                     'sent_consignee', 'sent_smartphone', 'sent_city', 'sent_district', 'sent_address', 'is_deliver',
                     'message', 'is_deliver']

    readonly_fields = []
    inlines = [GoodsDetailInline]

    form_layout = [
        Fieldset('收款开票公司信息',
                 Row('shop', 'company'),
                 'order_id', 'order_category', ),
        Fieldset('发票信息',
                 Row('title', 'tax_id'),
                 Row('phone', 'bank'),
                 'account', 'address', 'remark'),
        Fieldset('发货快递相关信息',
                 'is_deliver',
                 Row('sent_consignee', 'sent_smartphone'),
                 Row('sent_city', 'sent_district'),
                 'sent_address'),
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
        queryset = super(WOApplyAdmin, self).queryset()
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




# 发票工单创建界面
class WOUnhandleAdmin(object):
    list_display = ['company', 'order_id', 'process_tag', 'mistake_tag', 'memorandum', 'order_status', 'message',
                    'order_category', 'title', 'tax_id', 'phone', 'bank', 'account', 'address', 'remark', 'is_deliver',
                    'sent_consignee', 'sent_smartphone', 'sent_city', 'sent_district', 'sent_address', 'amount']
    actions = [SubmitWOAction, RejectSelectedAction, ]

    search_fields = ['order_id']
    list_filter = ['company__company_name', 'process_tag', 'mistake_tag', 'order_category', 'title', 'tax_id', 'amount']

    list_editable = ['order_category', 'title', 'tax_id', 'phone', 'bank', 'account', 'address', 'remark',
                     'sent_consignee', 'sent_smartphone', 'sent_city', 'sent_district', 'sent_address', 'is_deliver',
                     'message', 'is_deliver']

    readonly_fields = []
    inlines = [GoodsDetailInline]

    form_layout = [
        Fieldset('收款开票公司信息',
                 Row('shop', 'company'),
                 'order_id', 'order_category', ),
        Fieldset('发票信息',
                 Row('title', 'tax_id'),
                 Row('phone', 'bank'),
                 'account', 'address', 'remark'),
        Fieldset('发货快递相关信息',
                 'is_deliver',
                 Row('sent_consignee', 'sent_smartphone'),
                 Row('sent_city', 'sent_district'),
                 'sent_address'),
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
    list_display = ['company', 'order_id', 'process_tag', 'mistake_tag', 'message', 'memorandum',
                    'order_category', 'title', 'tax_id', 'phone', 'bank', 'account', 'address', 'remark',
                    'amount']

    actions = [CheckWOAction, SplitWOAction, RejectSelectedAction]
    inlines = [GoodsDetailInline]

    search_fields = ['order_id']
    list_filter = ['company__company_name', 'process_tag', 'mistake_tag', 'order_category', 'title', 'tax_id', 'amount']
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

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 发票工单查询界面
class WorkOrderAdmin(object):
    list_display = ['company', 'order_id', 'process_tag', 'mistake_tag', 'order_status', 'order_category', 'title',
                    'tax_id', 'phone', 'bank', 'account', 'address', 'remark', 'sent_consignee', 'sent_smartphone',
                    'sent_city', 'sent_district', 'sent_address', 'amount', 'is_deliver', 'message',
                    'memorandum']

    actions = []

    search_fields = ['order_id']
    list_filter = ['company__company_name', 'process_tag', 'mistake_tag', 'order_category', 'title', 'tax_id', 'amount',
                   'creator']
    readonly_fields = ['shop', 'company', 'order_id', 'order_category', 'title', 'tax_id', 'phone', 'bank', 'account',
                       'address', 'remark', 'sent_consignee', 'sent_smartphone', 'sent_city',
                       'sent_district', 'sent_address', 'amount', 'is_deliver', 'submit_time', 'handle_time',
                       'handle_interval', 'message', 'process_tag', 'mistake_tag', 'order_status']
    inlines = [GoodsDetailInline]

    form_layout = [
        Fieldset('收款开票公司信息',
                 Row('shop', 'company'),
                 'order_id', 'order_category', ),
        Fieldset('发票信息',
                 Row('title', 'tax_id'),
                 Row('phone', 'bank'),
                 'account', 'address', 'remark'),
        Fieldset('发货快递相关信息',
                 'is_deliver',
                 Row('sent_consignee', 'sent_smartphone'),
                 Row('sent_city', 'sent_district'),
                 'sent_address'),
        Fieldset(None,
                 'amount', 'submit_time', 'handle_time', 'handle_interval', 'memorandum', 'process_tag',
                 'mistake_tag', 'order_status', 'is_delete', 'creator',
                 **{"style": "display:None"}),
    ]

    def queryset(self):
        queryset = super(WorkOrderAdmin, self).queryset()
        queryset = queryset.filter(is_delete=0)
        return queryset


    def has_add_permission(self):
        # 禁用添加按钮
        return False




# 发票工单货品界面
class GoodsDetailAdmin(object):
    list_display = ['invoice', 'goods_id', 'goods_name', 'quantity', 'creator']
    readonly_fields = ['invoice', 'goods_id', 'goods_name', 'quantity', 'creator', 'is_delete', 'create_time',
                       'price', 'memorandum', 'update_time']

    def has_add_permission(self):
        # 禁用添加按钮
        return False

    def has_delete_permission(self):
        return False


class InvoiceGoodsInline(object):
    model = InvoiceGoods
    exclude = ['creator', 'goods_id', 'is_delete', 'order_id']

    extra = 0
    style = 'table'


# 发票订单处理界面
class IOhandleAdmin(object):
    list_display = ['company', 'order_id', 'process_tag', 'invoice_id', 'mistake_tag', 'order_status', 'message',
                    'memorandum', 'order_category', 'title', 'tax_id', 'phone', 'bank', 'account',
                    'address', 'remark', 'amount', 'ori_amount']
    list_editable = ['invoice_id', 'message']
    actions = [SubmitIOAction, RejectSelectedAction]
    search_fields = ['order_id']
    list_filter = ['company__company_name', 'process_tag', 'order_category', 'mistake_tag', 'title', 'tax_id', 'remark',
                   'amount', 'ori_amount']

    readonly_fields = ['shop', 'company', 'order_id', 'process_tag',  'mistake_tag', 'order_status', 'message',
                       'order_category', 'title','tax_id', 'phone', 'bank', 'account', 'ori_amount',
                       'address', 'remark', 'sent_consignee', 'sent_smartphone', 'memorandum', 'work_order',
                       'sent_province', 'sent_city', 'sent_district', 'sent_address', 'amount', 'is_deliver']
    inlines = [InvoiceGoodsInline]

    form_layout = [
        Fieldset('收款公司信息',
                 Row('shop', 'company'),
                 'order_category', ),
        Fieldset('发票信息',
                 Row('title', 'tax_id'),
                 Row('phone', 'bank', 'account'),
                 'address', 'remark'),
        Fieldset('单据金额',
                 Row('amount', 'ori_amount'),),
        Fieldset(None,
                 'order_id', 'amount', 'submit_time', 'handle_time', 'handle_interval', 'memorandum', 'process_tag',
                 'mistake_tag', 'order_status', 'is_delete', 'creator', 'track_no','is_deliver', 'sent_consignee',
                 'sent_smartphone', 'sent_province', 'sent_city', 'sent_district','sent_address', 'work_order',
                 'message', 'ori_amount', **{"style": "display:None"}),
    ]

    def queryset(self):
        queryset = super(IOhandleAdmin, self).queryset()
        queryset = queryset.filter(order_status=1, is_delete=0)
        return queryset

    def save_models(self):
        obj = self.new_obj
        if obj.invoice_id:
            obj.process_tag = 2
            obj.save()
        super().save_models()

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 申请人确认界面
class IOCheckAdmin(object):
    list_display = ['company', 'order_id', 'process_tag', 'mistake_tag', 'order_status', 'invoice_id', 'track_no',
                    'order_category', 'title', 'tax_id', 'amount', 'ori_amount', 'address', 'remark', 'is_deliver',
                    'sent_consignee', 'sent_smartphone', 'sent_address', 'message', 'memorandum']

    search_fields = ['order_id']
    list_filter = ['company__company_name', 'process_tag', 'order_category', 'mistake_tag', 'title', 'tax_id', 'remark',
                   'amount', 'ori_amount']
    actions = [CheckIOAction]
    readonly_fields = ['shop', 'company', 'order_id', 'process_tag',  'mistake_tag', 'order_status', 'message',
                       'order_category', 'title','tax_id', 'phone', 'bank', 'account', 'ori_amount', 'work_order',
                       'address', 'remark', 'sent_consignee', 'sent_smartphone', 'memorandum', 'invoice_id',
                       'sent_province', 'sent_city', 'sent_district', 'sent_address', 'amount', 'is_deliver']
    inlines = [InvoiceGoodsInline]

    form_layout = [
        Fieldset('收款开票公司信息',
                 'shop', 'company', 'order_id', 'order_category', ),
        Fieldset('发票信息',
                 'title', 'tax_id', 'phone', 'bank', 'account', 'address', 'remark'),
        Fieldset('发货快递相关信息',
                 'is_deliver', 'sent_consignee', 'sent_smartphone', 'sent_province', 'sent_city', 'sent_district',
                 'sent_address', 'track_no',),
        Fieldset(None,
                 'amount', 'submit_time', 'handle_time', 'handle_interval', 'memorandum', 'process_tag',
                 'mistake_tag', 'order_status', 'is_delete', 'creator',  'work_order',
                 **{"style": "display:None"}),
    ]

    def queryset(self):
        queryset = super(IOCheckAdmin, self).queryset()
        if self.request.user.is_superuser:
            queryset = queryset.filter(order_status=2, is_delete=0)
        else:
            queryset = queryset.filter(order_status=2, is_delete=0, creator=self.request.user.username)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False

    def has_delete_permission(self):
        return False


class InvoiceOrderAdmin(object):
    list_display = ['company', 'order_id', 'process_tag', 'mistake_tag', 'order_status', 'order_category', 'title',
                    'tax_id', 'phone', 'bank', 'account', 'ori_amount', 'address', 'remark', 'sent_consignee', 'sent_smartphone',
                    'sent_province', 'sent_city', 'sent_district', 'sent_address', 'amount', 'is_deliver', 'message',
                    'memorandum']

    search_fields = ['order_id']
    list_filter = ['company__company_name', 'process_tag', 'order_category', 'mistake_tag', 'title', 'tax_id', 'remark',
                   'amount', 'ori_amount', 'creator']
    readonly_fields = ['shop', 'company', 'order_id', 'process_tag',  'mistake_tag', 'order_status', 'message',
                       'order_category', 'title','tax_id', 'phone', 'bank', 'account', 'ori_amount', 'work_order',
                       'address', 'remark', 'sent_consignee', 'sent_smartphone', 'memorandum', 'invoice_id',
                       'sent_province', 'sent_city', 'sent_district', 'sent_address', 'amount', 'is_deliver']
    inlines = [InvoiceGoodsInline]

    form_layout = [
        Fieldset('收款开票公司信息',
                 'shop', 'company', 'order_id', 'order_category', ),
        Fieldset('发票信息',
                 'title', 'tax_id', 'phone', 'bank', 'account', 'address', 'remark'),
        Fieldset('发货快递相关信息',
                 'is_deliver', 'sent_consignee', 'sent_smartphone', 'sent_province', 'sent_city', 'sent_district',
                 'sent_address'),
        Fieldset('发票号及对应金额',
                 'invoice_id', 'amount', 'ori_amount'),
        Fieldset(None,
                 'submit_time', 'handle_time', 'handle_interval', 'memorandum', 'process_tag', 'message',
                 'mistake_tag', 'order_status', 'is_delete', 'creator', 'track_no', 'work_order',
                 **{"style": "display:None"}),
    ]

    def queryset(self):
        queryset = super(InvoiceOrderAdmin, self).queryset()
        if self.request.user.category == 1:
            queryset = queryset.filter(is_delete=0)
        else:
            queryset = queryset.filter(is_delete=0, creator=self.request.user.username)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False

    def has_delete_permission(self):
        return False


class InvoiceGoodsAdmin(object):
    list_display = ['invoice', 'goods_id', 'goods_name', 'quantity', 'creator']
    readonly_fields = ['invoice', 'goods_id', 'goods_name', 'quantity', 'creator', 'is_delete', 'create_time',
                       'price', 'memorandum', 'update_time']

    def has_delete_permission(self):
        return False


class DOCheckAdmin(object):
    list_display = ['order_status', 'process_tag', 'logistics', 'track_no', 'mistake_tag', 'memorandum', 'shop',
                    'ori_order_id', 'nickname', 'consignee', 'address', 'smartphone', 'condition_deliver', 'discounts',
                    'postage', 'receivable', 'goods_price', 'goods_amount',
                    'goods_id', 'goods_name', 'quantity', 'order_category', 'message', 'province', 'city', 'district']
    search_fields = ['track_no', 'ori_order_id']
    list_filter = ['logistics', 'shop', 'mistake_tag', 'process_tag', 'province', 'city', 'district']
    list_editable = ['logistics', 'track_no',]
    readonly_fields = ['order_status', 'process_tag', 'mistake_tag', 'memorandum', 'shop',
                       'ori_order_id', 'nickname', 'consignee', 'address', 'smartphone', 'condition_deliver', 'discounts',
                       'postage', 'receivable', 'goods_price', 'goods_amount',
                       'goods_id', 'goods_name', 'quantity', 'order_category', 'message', 'province', 'city', 'district']
    actions = [SubmitDOAction]
    ALLOWED_EXTENSIONS = ['xls', 'xlsx']
    INIT_FIELDS_DIC = {"原始单号": "ori_order_id", "快递公司": "logistics", "快递单号": "track_no"}
    import_data = True

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file', None)
        if file:
            result = self.handle_upload_file(request, file)
            self.message_user('导入成功数据%s条' % int(result['successful']), 'success')
            if result['false'] > 0 or result['error']:
                self.message_user('导入失败数据%s条,主要的错误是%s' % (int(result['false']), result['error']), 'warning')
            if result['repeated'] > 0:
                self.message_user('包含更新重复数据%s条' % int(result['repeated']), 'error')
        return super(DOCheckAdmin, self).post(request, *args, **kwargs)

    def handle_upload_file(self, request, _file):
        report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error": []}
        if '.' in _file.name and _file.name.rsplit('.')[-1] in self.__class__.ALLOWED_EXTENSIONS:
            df = pd.read_excel(_file, sheet_name=0)

            # 获取表头，对表头进行转换成数据库字段名
            columns_key = df.columns.values.tolist()
            for i in range(len(columns_key)):
                if self.__class__.INIT_FIELDS_DIC.get(columns_key[i], None) is not None:
                    columns_key[i] = self.__class__.INIT_FIELDS_DIC.get(columns_key[i])

            # 验证一下必要的核心字段是否存在
            _ret_verify_field = DOCheck.verify_mandatory(columns_key)
            if _ret_verify_field is not None:
                return _ret_verify_field

            # 更改一下DataFrame的表名称
            columns_key_ori = df.columns.values.tolist()
            ret_columns_key = dict(zip(columns_key_ori, columns_key))
            df.rename(columns=ret_columns_key, inplace=True)

            # 更改一下DataFrame的表名称
            num_end = 0
            step = 300
            step_num = int(len(df) / step) + 2
            i = 1
            while i < step_num:
                num_start = num_end
                num_end = step * i
                intermediate_df = df.iloc[num_start: num_end]

                # 获取导入表格的字典，每一行一个字典。这个字典最后显示是个list
                _ret_list = intermediate_df.to_dict(orient='records')
                intermediate_report_dic = self.save_resources(request, _ret_list)
                for k, v in intermediate_report_dic.items():
                    if k == "error":
                        if intermediate_report_dic["error"]:
                            report_dic[k].append(v)
                    else:
                        report_dic[k] += v
                i += 1
            return report_dic
        # 以下是csv处理逻辑，和上面的处理逻辑基本一致。
        elif '.' in _file.name and _file.name.rsplit('.')[-1] == 'csv':
            df = pd.read_csv(_file, encoding="GBK", chunksize=300)

            for piece in df:
                # 获取表头
                columns_key = piece.columns.values.tolist()
                # 剔除表头中特殊字符等于号和空格
                for i in range(len(columns_key)):
                    columns_key[i] = columns_key[i].replace(' ', '').replace('=', '')
                # 循环处理对应的预先设置，转换成数据库字段名称
                for i in range(len(columns_key)):
                    if self.__class__.INIT_FIELDS_DIC.get(columns_key[i], None) is not None:
                        columns_key[i] = self.__class__.INIT_FIELDS_DIC.get(columns_key[i])
                # 直接调用验证函数进行验证
                _ret_verify_field = DOCheck.verify_mandatory(columns_key)
                if _ret_verify_field is not None:
                    return _ret_verify_field
                # 验证通过进行重新处理。
                columns_key_ori = piece.columns.values.tolist()
                ret_columns_key = dict(zip(columns_key_ori, columns_key))
                piece.rename(columns=ret_columns_key, inplace=True)
                _ret_list = piece.to_dict(orient='records')
                intermediate_report_dic = self.save_resources(request, _ret_list)
                for k, v in intermediate_report_dic.items():
                    if k == "error":
                        if intermediate_report_dic["error"]:
                            report_dic[k].append(v)
                    else:
                        report_dic[k] += v
            return report_dic

        else:
            report_dic["error"].append('只支持excel和csv文件格式！')
            return report_dic

    @staticmethod
    def save_resources(request, resource):
        # 设置初始报告
        report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error":[]}

        # 开始导入数据
        for row in resource:
            # 字符串字段去特殊字符
            for key, value in row.items():
                row[key] = str(value).replace(' ', '').replace("'", '').replace('\n', '')
            _q_deliver_order = DeliverOrder.objects.filter(ori_order_id=row['ori_order_id'])
            if _q_deliver_order.exists():
                deliver_order = _q_deliver_order[0]
                deliver_order.logistics = row['logistics']
                deliver_order.track_no = row['track_no']

            else:
                report_dic["discard"] += 1
                report_dic["error"].append("%s原始单号无法找到发货单" % row['ori_order_id'])
                continue

            try:
                deliver_order.process_tag = 1
                deliver_order.save()
                report_dic["successful"] += 1
            # 保存出错，直接错误条数计数加一。
            except Exception as e:
                report_dic["false"] += 1
                report_dic["error"].append(e)
        return report_dic

    def queryset(self):
        queryset = super(DOCheckAdmin, self).queryset()
        queryset = queryset.filter(order_status=1, is_delete=0)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False

    def has_delete_permission(self):
        return False


class DeliverOrderAdmin(object):
    list_display = ['order_status', 'logistics', 'track_no', 'shop', 'ori_order_id', 'nickname', 'consignee', 'address',
                    'smartphone', 'condition_deliver', 'discounts', 'postage', 'receivable', 'goods_price', 'goods_amount',
                    'goods_id', 'goods_name', 'quantity', 'order_category', 'message', 'province', 'city', 'district']

    readonly_fields = ['order_status', 'process_tag', 'mistake_tag', 'memorandum', 'shop', 'logistics', 'track_no',
                       'ori_order_id', 'nickname', 'consignee', 'address', 'smartphone', 'condition_deliver', 'discounts',
                       'postage', 'receivable', 'goods_price', 'goods_amount',
                       'goods_id', 'goods_name', 'quantity', 'order_category', 'message', 'province', 'city', 'district']

    search_fields = ['track_no', 'ori_order_id']
    list_filter = ['logistics', 'shop', 'mistake_tag', 'process_tag', 'province', 'city', 'district']


    def has_add_permission(self):
        # 禁用添加按钮
        return False


    def has_delete_permission(self):
        return False


# 发票工单操作
xadmin.site.register(WOUnhandle, WOUnhandleAdmin)
xadmin.site.register(WOCheck, WOCheckAdmin)
# 发票订单操作
xadmin.site.register(IOhandle, IOhandleAdmin)
xadmin.site.register(IOCheck, IOCheckAdmin)
# 物流发货单操作
xadmin.site.register(DOCheck, DOCheckAdmin)
xadmin.site.register(DeliverOrder, DeliverOrderAdmin)
# 工单和订单的查询
xadmin.site.register(WorkOrder, WorkOrderAdmin)
xadmin.site.register(InvoiceOrder, InvoiceOrderAdmin)
# 货品相关信息
xadmin.site.register(GoodsDetail, GoodsDetailAdmin)
xadmin.site.register(InvoiceGoods, InvoiceGoodsAdmin)