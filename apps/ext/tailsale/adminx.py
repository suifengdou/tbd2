# -*- coding: utf-8 -*-
# @Time    : 2020/7/4 9:50
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

import math, re, operator
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
import numpy as np
import xadmin
from xadmin.plugins.actions import BaseActionView
from xadmin.views.base import filter_hook
from xadmin.util import model_ngettext
from xadmin.layout import Fieldset, Main, Row, Side


from .models import OriTailOrder, OTOUnhandle, OTOCheck, OTOGoods, TailOrder, TOhandle, TOSpecialhandle, TOCheck, TOGoods
from apps.utils.geography.models import DistrictInfo
from apps.base.shop.models import ShopInfo
from apps.base.company.models import MainInfo
from apps.base.goods.models import MachineInfo
from apps.utils.geography.models import CityInfo
from apps.users.models import UserProfile


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
                if isinstance(obj, OriTailOrder):
                    if obj.order_status > 0:
                        obj.order_status -= 1
                        obj.process_tag = 5
                        obj.save()
                        if obj.order_status == 0:
                            obj.otogoods_set.all().update(order_status=0)
                            self.message_user("%s 取消成功" % obj.order_id, "success")
                        else:
                            self.message_user("%s 驳回上一级成功" % obj.order_id, "success")
                    else:
                        n -= 1
                        self.message_user("%s 单据状态错误，请检查，驳回出错。" % obj.order_id, "error")

                    # for obj in queryset:
                    #     mistake_tag = 0
                    #     _q_invoice_orders = obj.work_order.invoiceorder_set.all()
                    #     for invoice_order in _q_invoice_orders:
                    #         if invoice_order.order_status == 2:
                    #             n -= 1
                    #             self.message_user("%s 请确保此工单所有的发票订单都为未开票状态。" % obj.work_order, "error")
                    #             mistake_tag = 1
                    #             continue
                    #     if mistake_tag:
                    #         continue
                    #     else:
                    #
                    #         for invoice_order in _q_invoice_orders:
                    #             try:
                    #                 invoice_order.invoicegoods_set.all().delete()
                    #             except Exception as e:
                    #                 self.message_user("%s 删除货品信息失败。错误：%s" % (invoice_order, e), "error")
                    #                 mistake_tag = 1
                    #                 continue
                    #         if mistake_tag:
                    #             self.message_user("%s 此订单驳回出错，需要联系管理员。" % obj.work_order, "error")
                    #             obj.mistake_tag = 4
                    #             obj.save()
                    #             continue
                    #
                    #         obj.work_order.order_status = 2
                    #         obj.work_order.process_tag = 5
                    #         obj.work_order.mistake_tag = 12
                    #         obj.work_order.save()
                    #
                    #         try:
                    #             _q_invoice_orders.delete()
                    #         except Exception as e:
                    #             self.message_user("删除订单失败。错误：%s" % e, "error")
                    #             obj.mistake_tag = 4
                    #             obj.save()
                    #             continue
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
class SubmitOTOAction(BaseActionView):
    action_name = "submit_oto"
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
                    check_fields = ['order_id', 'sent_consignee', 'sent_smartphone', 'sent_district', 'sent_address']
                    for key in check_fields:
                        value = getattr(obj, key, None)
                        if value:
                            setattr(obj, key, str(value).replace(' ', '').replace("'", '').replace('\n', ''))

                    if not obj.sign_company:
                        self.message_user("%s 账号没有设置公司" % obj.order_id, "error")
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
                    if not re.match(r'^[0-9-]+$', obj.sent_smartphone):
                        self.message_user("%s 收件人手机错误" % obj.order_id, "error")
                        obj.mistake_tag = 3
                        obj.save()
                        n -= 1
                        continue
                    if not re.match("^[0-9A-Za-z]+$", obj.order_id):
                        self.message_user("%s 单号只支持数字和英文字母" % obj.order_id, "error")
                        obj.mistake_tag = 4
                        obj.save()
                        n -= 1
                        continue
                    obj.submit_time = datetime.datetime.now()
                    obj.order_status = 2
                    obj.mistake_tag = 0
                    obj.process_tag = 0
                    obj.save()

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


# 审核不用拆单工单
class SetOTOAction(BaseActionView):
    action_name = "set_logistics_oto"
    description = "设置订单为物流发货"
    model_perm = 'change'
    icon = "fa fa-check-square-o"


    @filter_hook
    def do_action(self, queryset):
        if not self.has_change_permission():
            raise PermissionDenied
        n = queryset.count()
        if n:
            self.log('change',
                     '批量审核了 %(count)d %(items)s.' % {"count": n, "items": model_ngettext(self.opts, n)})
            queryset.update(process_tag=6)

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


# 审核不用拆单工单
class CheckOTOAction(BaseActionView):
    action_name = "submit_single_oto"
    description = "提交不拆单的订单"
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
                    if int(obj.quantity) > 1 and obj.process_tag != 6:
                        self.message_user("%s 需要拆单的订单，用拆单递交，如发物流设置标记物流订单" % obj.order_id, "error")
                        obj.mistake_tag = 5
                        obj.save()
                        n -= 1
                        continue

                    tail_order = TailOrder()
                    copy_fields_order = ['shop', 'order_id', 'order_category', 'sent_consignee', 'sent_smartphone',
                                         'sent_city', 'sent_district', 'sent_address', 'amount',
                                         'message', 'creator', 'sign_company', 'sign_department']

                    for key in copy_fields_order:
                        value = getattr(obj, key, None)
                        setattr(tail_order, key, value)

                    tail_order.sent_province = obj.sent_city.province
                    tail_order.creator = obj.creator
                    tail_order.ori_amount = obj.amount
                    tail_order.work_order = obj
                    try:
                        tail_order.save()
                    except Exception as e:
                        self.message_user("%s 递交订单出错 %s" % (obj.order_id, e), "error")
                        obj.mistake_tag = 6
                        obj.save()
                        n -= 1
                        continue
                    _q_goods = obj.otogoods_set.all()
                    for good in _q_goods:
                        to_good = TOGoods()
                        to_good.tail_order = tail_order
                        to_good.goods_nickname = good.goods_name.goods_name
                        copy_fields_goods = ['goods_id', 'goods_name', 'quantity', 'price', 'memorandum']
                        for key in copy_fields_goods:
                            value = getattr(good, key, None)
                            setattr(to_good, key, value)
                        try:
                            to_good.amount = to_good.quantity * to_good.price
                            to_good.settlement_price = to_good.price * obj.sign_company.discount_rate
                            to_good.settlement_amount = to_good.settlement_price * to_good.quantity
                            to_good.creator = obj.creator
                            to_good.save()
                        except Exception as e:
                            self.message_user("%s 生成订单货品出错 %s" % (obj.order_id, e), "error")
                            obj.mistake_tag = 7
                            obj.save()
                            continue

                    obj.order_status = 3
                    obj.mistake_tag = 0
                    obj.process_tag = 2

                    obj.save()

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
                            copy_fields_order = ['shop', 'company', 'order_category', 'title', 'tax_id', 'phone',
                                                 'bank', 'account', 'address', 'remark', 'sent_consignee',
                                                 'sent_smartphone', 'sent_city', 'sent_district', 'sent_address',
                                                 'is_deliver', 'message', 'sign_company', 'sign_department', 'creator',
                                                 'nickname']
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
                                goods_order.goods_nickname = goods.goods_name
                                goods_order.goods_id = goods.goods_id
                                goods_order.quantity = detail[0]
                                goods_order.price = detail[1]
                                goods_order.memorandum = '来源 %s 的第 %s 张发票' % (obj.order_id, invoice_num + 1)

                                try:
                                    goods_order.creator = obj.creator
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
                        obj.mistake_tag = 0
                        obj.process_tag = 6
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
                    _q_creator_order = DeliverOrder.objects.filter(creator=obj.creator, order_status=1)
                    if _q_creator_order.exists():
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
                                invoice_num = int(re.findall(r'共(\d+)张', deliver_order.message)[0])
                                if invoice_num < 3:
                                    invoice_num += 1
                                    ori_order_id = '%s,%s' % (deliver_order.ori_order_id, obj.invoice_id)
                                    deliver_order.ori_order_id = ori_order_id
                                    deliver_order.message = '%s%s共%s张' % (obj.sign_department.name, obj.creator, invoice_num)
                                else:
                                    invoice_num += 1
                                    deliver_order.message = '%s%s共%s张(发票号最大显示3个，完整见UT发票订单)' % \
                                                            (obj.sign_department.name, obj.creator, invoice_num)
                                deliver_order.save()
                                obj.order_status = 2
                                obj.mistake_tag = 0
                                obj.save()
                                continue
                        _q_repeat_order = DeliverOrder.objects.filter(consignee=obj.sent_consignee,
                                                                      smartphone=obj.sent_smartphone,
                                                                      address=obj.sent_address,
                                                                      order_status=1)
                        if _q_repeat_order.exists():
                            repeat_order = _q_repeat_order[0]
                            if str(obj.invoice_id) in str(repeat_order.ori_order_id):
                                self.message_user("%s 重复递交了订单" % obj.order_id, "error")
                                obj.order_status = 2
                                obj.mistake_tag = 0
                                obj.save()
                                n -= 1
                                continue
                            else:
                                ori_order_id = '%s,%s' % (repeat_order.ori_order_id, obj.invoice_id)
                                invoice_num = len(ori_order_id.split(','))
                                if invoice_num < 4:
                                    repeat_order.ori_order_id = ori_order_id
                                    repeat_order.message = '%s%s共%s张' % \
                                                           (obj.sign_department.name, obj.creator, invoice_num)
                                else:
                                    repeat_order.message = '%s%s共%s张(发票号最大显示3个，完整见UT发票订单)' % \
                                                           (obj.sign_department.name, obj.creator, invoice_num)
                                repeat_order.save()
                                obj.order_status = 2
                                obj.mistake_tag = 0
                                obj.save()
                                continue

                    deliver_order = DeliverOrder()

                    if obj.nickname:
                        deliver_order.nickname = obj.nickname
                    else:
                        deliver_order.nickname = obj.sent_consignee
                    deliver_order.work_order = obj.work_order
                    deliver_order.shop = obj.shop.shop_name
                    deliver_order.ori_order_id = obj.invoice_id
                    deliver_order.province = obj.sent_city.province.province
                    deliver_order.city = obj.sent_city.city

                    deliver_order.consignee = obj.sent_consignee
                    deliver_order.smartphone = obj.sent_smartphone
                    deliver_order.message = '%s%s共1张' % (obj.sign_department.name, obj.creator)
                    deliver_order.address = obj.sent_address
                    deliver_order.creator = obj.creator

                    if obj.is_deliver == 1:
                        deliver_order.logistics = '顺丰'
                    else:
                        deliver_order.logistics = '申通'
                    deliver_order.remark = deliver_order.logistics
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


class OTOGoodsInline(object):
    model = OTOGoods
    exclude = ['creator', 'goods_id', 'is_delete', 'order_id']

    extra = 1
    style = 'table'


# 原始尾货订单创建并提交界面
class OTOUnhandleAdmin(object):
    list_display = ['shop', 'order_id', 'amount', 'order_category', 'mode_warehouse', 'sent_consignee', 'sent_smartphone',
                    'sent_city', 'sent_district', 'sent_address', 'submit_time', 'handle_time', 'handle_interval',
                    'message', 'feedback', 'sign_company', 'sign_department', 'process_tag', 'mistake_tag',
                    'order_status']
    actions = [SubmitOTOAction, RejectSelectedAction]

    search_fields = ['order_id']
    list_filter = ['mode_warehouse', 'process_tag', 'creator', 'mistake_tag', 'order_category']

    list_editable = ['order_category', 'mode_warehouse', 'sent_consignee', 'sent_smartphone', 'sent_city', 'sent_district',
                     'sent_address', 'message',]

    readonly_fields = []
    inlines = [OTOGoodsInline]
    import_data = True

    def post(self, request, *args, **kwargs):

        file = request.FILES.get('file', None)
        if file:
            result = self.handle_upload_file(file)
            if isinstance(result, int):
                self.message_user('导入成功数据%s条' % result['successful'], 'success')
                if result['false'] > 0:
                    self.message_user('导入失败数据%s条,主要的错误是%s' % (result['false'], result['error']), 'warning')
                if result['repeated'] > 0:
                    self.message_user('包含更新重复数据%s条' % result['repeated'], 'error')
            else:
                self.message_user('结果提示：%s' % result)
        return super(OTOUnhandleAdmin, self).post(request, *args, **kwargs)

    def handle_upload_file(self, _file):
        INIT_FIELDS_DIC = {
            '店铺': 'shop',
            '收款开票公司': 'company',
            '收件人姓名': 'sent_consignee',
            '收件人手机': 'sent_smartphone',
            '收件城市': 'sent_city',
            '收件区县': 'sent_district',
            '收件地址': 'sent_address',
            '是否发顺丰': 'is_deliver',
            '工单留言': 'message',
            '货品编码': 'goods_id',
            '货品名称': 'goods_name',
            '数量': 'quantity',
            '含税单价': 'price',
            '用户昵称': 'nickname',
        }
        ALLOWED_EXTENSIONS = ['xls', 'xlsx']
        report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error": []}

        if '.' in _file.name and _file.name.rsplit('.')[-1] in ALLOWED_EXTENSIONS:
            with pd.ExcelFile(_file) as xls:
                df = pd.read_excel(xls, sheet_name=0, converters={u'货品编码': str})
                FILTER_FIELDS = ['店铺', '收件人姓名', '收件人手机', '收件城市', '收件区县', '收件地址',
                                 '是否发顺丰', '工单留言', '货品编码', '货品名称', '数量', '含税单价','用户昵称']

                try:
                    df = df[FILTER_FIELDS]
                except Exception as e:
                    report_dic["error"].append(e)
                    return report_dic


                # 获取表头，对表头进行转换成数据库字段名
                columns_key = df.columns.values.tolist()
                for i in range(len(columns_key)):
                    columns_key[i] = columns_key[i].replace(' ', '').replace('=', '')

                for i in range(len(columns_key)):
                    if INIT_FIELDS_DIC.get(columns_key[i], None) is not None:
                        columns_key[i] = INIT_FIELDS_DIC.get(columns_key[i])

                # 验证一下必要的核心字段是否存在
                _ret_verify_field = OriTailOrder.verify_mandatory(columns_key)
                if _ret_verify_field is not None:
                    report_dic["error"].append(str(_ret_verify_field))
                    return report_dic

                # 更改一下DataFrame的表名称
                columns_key_ori = df.columns.values.tolist()
                ret_columns_key = dict(zip(columns_key_ori, columns_key))
                df.rename(columns=ret_columns_key, inplace=True)
                check_list = ['shop', 'company', 'order_id', 'order_category', 'sent_consignee', 'sent_smartphone',
                              'sent_city', 'sent_district', 'sent_address', 'is_deliver', 'goods_id']
                df_check = df[check_list]

                tax_ids = list(set(df_check.tax_id))
                for tax_id in tax_ids:
                    data_check = df_check[df_check.tax_id == tax_id]
                    check_list.pop()
                    if len(data_check.goods_id) != len(list(set(data_check.goods_id))):
                        error = '税号%s，货品重复，请剔除重复货品' % str(tax_id)
                        report_dic["error"].append(error)
                        return report_dic
                    for word in check_list:
                        check_word = data_check[word]
                        if np.any(check_word.isnull() == True):
                            continue
                        check_word = list(set(check_word))
                        if len(check_word) > 1:
                            error = '税号%s的%s不一致，相同税号%s必须相同' % (str(tax_id), str(word), str(word))
                            report_dic["error"].append(error)
                            return report_dic

                # 获取导入表格的字典，每一行一个字典。这个字典最后显示是个list
                for tax_id in tax_ids:
                    df_invoice = df[df.tax_id == tax_id]
                    _ret_list = df_invoice.to_dict(orient='records')
                    intermediate_report_dic = self.save_resources(_ret_list)
                    for k, v in intermediate_report_dic.items():
                        if k == "error":
                            if intermediate_report_dic["error"]:
                                report_dic[k].append(v)
                        else:
                            report_dic[k] += v
                return report_dic

        else:
            error = "只支持excel文件格式！"
            report_dic["error"].append(error)
            return report_dic

    def save_resources(self, resource):
        # 设置初始报告
        report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error": []}

        work_order = OriTailOrder()

        if not re.match(r'^[0-9A-Z]+$', resource[0]['order_id']):
            error = '源单号%s非法，请使用正确的源单号格式（只支持英文字母和数字组合）' % resource[0]['order_id']
            report_dic['error'].append(error)
            return report_dic
        else:
            work_order.order_id = resource[0]['order_id']

        _q_work_order = OriTailOrder.objects.filter(order_id=resource[0]['order_id'])
        if not _q_work_order.exists():
            # 开始导入数据
            check_list = ['title', 'tax_id',  'sent_consignee', 'sent_smartphone', 'sent_district', 'sent_address',
                          'phone', 'bank', 'account', 'address', 'remark', 'message', 'nickname']

            _q_shop = ShopInfo.objects.filter(shop_name=resource[0]['shop'])
            if _q_shop.exists():
                work_order.shop = _q_shop[0]
            else:
                error = '店铺%s不存在，请使用正确的店铺名' % resource[0]['shop']
                report_dic['error'].append(error)
                return report_dic
            _q_company = MainInfo.objects.filter(company_name=resource[0]['company'])
            if _q_company.exists():
                work_order.company = _q_company[0]
            else:
                error = '开票公司%s不存在，请使用正确的公司名' % resource[0]['company']
                report_dic['error'].append(error)
                return report_dic
            category = {
                '专票': 1,
                '普票': 2,
            }
            order_category = category.get(resource[0]['order_category'], None)
            if order_category:
                work_order.order_category = order_category

            else:
                error = '开票类型%s不存在，请使用正确的开票类型' % resource[0]['order_category']
                report_dic['error'].append(error)
                return report_dic



            _q_city = CityInfo.objects.filter(city=resource[0]['sent_city'])
            if _q_city.exists():
                work_order.sent_city = _q_city[0]
            else:
                error = '城市%s非法，请使用正确的二级城市名称' % resource[0]['sent_city']
                report_dic['error'].append(error)
                return report_dic

            logical_decision = {
                '是': 1,
                '否': 0,
            }
            is_deliver = logical_decision.get(resource[0]['is_deliver'], None)
            if is_deliver is None:
                error = '是否发顺丰字段：%s非法（只可以填是否）' % resource[0]['is_deliver']
                report_dic['error'].append(error)
                return report_dic
            else:
                work_order.is_deliver = is_deliver

            if order_category == 1:
                check_list = check_list[:10]
                for k in check_list:
                    if not resource[0][k]:
                        error = '%s非法，开专票请把必填项补全' % k
                        report_dic['error'].append(error)
                        return report_dic
            elif order_category == 2:
                check_list = check_list[:6]
                for k in check_list:
                    if not resource[0][k]:
                        error = '%s非法，开普票请把必填项补全' % k
                        report_dic['error'].append(error)
                        return report_dic
            if self.request.user.company:
                work_order.sign_company = self.request.user.company
            else:
                error = '账号公司未设置或非法，联系管理员处理'
                report_dic['error'].append(error)
                return report_dic

            if self.request.user.department:
                work_order.sign_department = self.request.user.department
            else:
                error = '账号部门未设置或非法，联系管理员处理'
                report_dic['error'].append(error)
                return report_dic

            for attr in check_list:
                if resource[0][attr]:
                    setattr(work_order, attr, resource[0][attr])

            try:
                work_order.creator = self.request.user.username
                work_order.save()
                report_dic["successful"] += 1
            # 保存出错，直接错误条数计数加一。
            except Exception as e:
                report_dic["error"].append(e)
                report_dic["false"] += 1
                return report_dic
        else:
            work_order = _q_work_order[0]
            if work_order.order_status != 1:
                error = '此订单%s已经存在，请核实再导入' % (work_order.order_id)
                report_dic["error"].append(error)
                report_dic["false"] += 1
                return report_dic
            all_goods_info = work_order.goodsdetail_set.all()
            all_goods_info.delete()

        goods_ids = [row['goods_id'] for row in resource]
        goods_quantity = [row['quantity'] for row in resource]
        goods_prices = [row['price'] for row in resource]

        for goods_id, quantity, price in zip(goods_ids, goods_quantity, goods_prices):
            goods_order = OTOGoods()
            _q_goods_id = MachineInfo.objects.filter(goods_id=goods_id)
            if _q_goods_id.exists():
                goods_order.goods_name = _q_goods_id[0]
                goods_order.goods_id = goods_id
                goods_order.quantity = quantity
                goods_order.price = price
                goods_order.invoice = work_order
                goods_order.creator = self.request.user.username
                try:
                    goods_order.save()
                    report_dic["successful"] += 1
                # 保存出错，直接错误条数计数加一。
                except Exception as e:
                    report_dic["error"].append(e)
                    report_dic["false"] += 1
                    work_order.mistake_tag = 15
                    work_order.save()
                    return report_dic
            else:
                error = '发票工单的货品编码错误，请处理好编码再导入'
                report_dic["error"].append(error)
                report_dic["false"] += 1
                work_order.mistake_tag = 15
                work_order.save()
                return report_dic

        return report_dic

    form_layout = [
        Fieldset('基本信息',
                 Row('shop', 'sign_company'),
                 'order_id',
                 'order_category', ),
        Fieldset('发货相关信息',
                 Row('sent_consignee', 'sent_smartphone'),
                 Row('sent_city', 'sent_district'),
                 'sent_address'),
        Fieldset(None,
                 'submit_time', 'handle_time', 'handle_interval', 'feedback', 'process_tag', 'amount',
                 'mistake_tag', 'order_status', 'is_delete', 'creator', 'sign_company', 'sign_department',
                 **{"style": "display:None"}),
    ]

    def save_models(self):
        obj = self.new_obj
        request = self.request
        obj.creator = request.user.username
        if not obj.sign_company:
            if request.user.company:
                obj.sign_company = request.user.company
        if not obj.sign_department:
            obj.sign_department = request.user.department
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
        queryset = super(OTOUnhandleAdmin, self).queryset()
        queryset = queryset.filter(order_status=1, is_delete=0)

        for obj in queryset:
            try:
                amount = obj.otogoods_set.all().aggregate(
                    sum_product=Sum(F("quantity") * F('price'), output_field=models.FloatField()))["sum_product"]
            except Exception as e:
                amount = 0
            if amount is None:
                amount = 0
            obj.amount = amount
            obj.save()
        return queryset


class OTOCheckAdmin(object):
    list_display = ['shop', 'order_id', 'amount', 'order_category', 'mode_warehouse', 'feedback', 'sent_consignee',
                    'sent_smartphone', 'sent_city', 'sent_district', 'sent_address', 'submit_time', 'handle_time',
                    'handle_interval', 'message',  'sign_company', 'sign_department', 'process_tag', 'mistake_tag',
                    'order_status']
    actions = [SetOTOAction, CheckOTOAction, RejectSelectedAction,]

    search_fields = ['order_id']
    list_filter = ['mode_warehouse', 'process_tag', 'creator', 'mistake_tag', 'order_category', 'sent_smartphone',
                   'submit_time', 'create_time']

    list_editable = ['feedback']
    readonly_fields = ['shop', 'sign_company', 'order_id', 'sent_city', 'sent_district', 'sent_address', 'message',
                       'sent_consignee', 'order_category', 'sent_smartphone', 'mode_warehouse',]

    inlines = [OTOGoodsInline]
    import_data = True

    form_layout = [
        Fieldset('可编辑信息',
                 'feedback', ),
        Fieldset('基本信息',
                 Row('shop', 'sign_company'),
                 'order_id',
                 'order_category', ),
        Fieldset('发货相关信息',
                 Row('sent_consignee', 'sent_smartphone'),
                 Row('sent_city', 'sent_district'),
                 'sent_address'),
        Fieldset(None,
                 'submit_time', 'handle_time', 'handle_interval', 'process_tag', 'amount',
                 'mistake_tag', 'order_status', 'is_delete', 'creator', 'sign_company', 'sign_department',
                 **{"style": "display:None"}),
    ]

    def queryset(self):
        queryset = super(OTOCheckAdmin, self).queryset()
        queryset = queryset.filter(order_status=2, is_delete=0)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


class OriTailOrderAdmin(object):
    list_display = ['shop', 'order_id', 'amount', 'order_category', 'mode_warehouse', 'feedback', 'sent_consignee',
                    'sent_smartphone', 'sent_city', 'sent_district', 'sent_address', 'submit_time', 'handle_time',
                    'handle_interval', 'message',  'sign_company', 'sign_department', 'process_tag', 'mistake_tag',
                    'order_status']

    search_fields = ['order_id']
    list_filter = ['process_tag', 'mode_warehouse', 'creator', 'sent_smartphone', 'mistake_tag', 'order_category',
                   'create_time', 'submit_time', 'sign_company__company_name', ]

    readonly_fields = ['shop', 'order_id', 'amount', 'order_category', 'mode_warehouse', 'feedback', 'sent_consignee',
                       'sent_smartphone', 'sent_city', 'sent_district', 'sent_address', 'submit_time', 'handle_time',
                       'handle_interval', 'message',  'sign_company', 'sign_department', 'process_tag', 'mistake_tag',
                       'order_status']

    inlines = [OTOGoodsInline]
    import_data = True

    form_layout = [
        Fieldset('基本信息',
                 Row('shop', 'sign_company'),
                 'order_id',
                 'order_category', ),
        Fieldset('发货相关信息',
                 Row('sent_consignee', 'sent_smartphone'),
                 Row('sent_city', 'sent_district'),
                 'sent_address'),
        Fieldset(None,
                'handle_interval', 'process_tag', 'mistake_tag', 'is_delete', 'creator', 'sign_company',
                 'sign_department', **{"style": "display:None"}),
    ]

    def has_add_permission(self):
        # 禁用添加按钮
        return False


class OTOGoodsAdmin(object):
    list_display = ['order_status', 'ori_tail_order', 'sent_consignee', 'sent_smartphone', 'sent_address', 'shop',
                    'goods_name', 'quantity', 'price', 'amount']
    readonly_fields = ['order_status', 'ori_tail_order', 'goods_id', 'goods_name', 'quantity', 'price', 'memorandum']
    list_filter = ['order_status', 'ori_tail_order__order_id', 'ori_tail_order__sent_smartphone', 'goods_id',
                   'goods_name', 'quantity', 'price', 'create_time', 'creator']
    search_fields = ['ori_tail_order__order_id']

    def has_add_permission(self):
        # 禁用添加按钮
        return False


class TOGoodsInline(object):
    model = TOGoods
    exclude = ['creator', 'goods_id', 'is_delete', 'order_id']

    extra = 1
    style = 'table'


class TOhandleAdmin(object):
    list_display = ['shop', 'order_id', 'amount', 'order_category', 'mode_warehouse', 'feedback', 'sent_consignee',
                    'sent_smartphone', 'sent_city', 'sent_district', 'sent_address', 'submit_time', 'handle_time',
                    'handle_interval', 'message',  'sign_company', 'sign_department', 'process_tag', 'mistake_tag',
                    'order_status']
    actions = [RejectSelectedAction,]

    search_fields = ['order_id']
    list_filter = ['mode_warehouse', 'process_tag', 'creator', 'mistake_tag', 'order_category', 'sent_smartphone',
                   'submit_time', 'create_time']

    list_editable = ['feedback']
    readonly_fields = ['shop', 'sign_company', 'order_id', 'sent_city', 'sent_district', 'sent_address', 'message',
                       'sent_consignee', 'order_category', 'sent_smartphone', 'mode_warehouse',]

    inlines = [OTOGoodsInline]
    import_data = True

    form_layout = [
        Fieldset('可编辑信息',
                 'feedback', ),
        Fieldset('基本信息',
                 Row('shop', 'sign_company'),
                 'order_id',
                 'order_category', ),
        Fieldset('发货相关信息',
                 Row('sent_consignee', 'sent_smartphone'),
                 Row('sent_city', 'sent_district'),
                 'sent_address'),
        Fieldset(None,
                 'submit_time', 'handle_time', 'handle_interval', 'process_tag', 'amount',
                 'mistake_tag', 'order_status', 'is_delete', 'creator', 'sign_company', 'sign_department',
                 **{"style": "display:None"}),
    ]

    def queryset(self):
        queryset = super(TOhandleAdmin, self).queryset()
        queryset = queryset.filter(order_status=2, is_delete=0)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


class TOSpecialhandleAdmin(object):
    pass


class TOCheckAdmin(object):
    pass


class TailOrderAdmin(object):
    pass


class TOGoodsAdmin(object):
    pass


xadmin.site.register(OTOUnhandle, OTOUnhandleAdmin)
xadmin.site.register(OTOCheck, OTOCheckAdmin)
xadmin.site.register(OriTailOrder, OriTailOrderAdmin)
xadmin.site.register(OTOGoods, OTOGoodsAdmin)
xadmin.site.register(TOhandle, TOhandleAdmin)