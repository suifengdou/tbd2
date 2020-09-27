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


from .models import OriTailOrder, OTOUnhandle, OTOCheck, OTOGoods, TailOrder, TOhandle, TOSpecialhandle, TOGoods
from .models import PayBillOrder, PBOSubmit, PBOCheck, PBOGoods, TOHGoods, TOSGoods, TOPrivilegeGoods
from .models import AccountInfo, AccountCheck, AccountUnfinished, PBillToAccount, AccountSpecialCheck
from .models import FSCheck, FSSpecialCheck, FSSubmit, FinalStatement, FinalStatementGoods, FSAffirm, FSSpecialAffirm
from .models import ROHandle, ROCheck, RefundOrder, ROGCheck, ROGoods
from .models import ABOSubmit, ABOCheck, ArrearsBillOrder, ABOGoods, ABillToAccount, TailPartsOrder, SubmitTPO
from apps.assistants.giftintalk.models import GiftOrderInfo
from apps.utils.geography.models import DistrictInfo
from apps.base.shop.models import ShopInfo
from apps.base.company.models import MainInfo
from apps.base.goods.models import MachineInfo, GoodsInfo
from apps.utils.geography.models import CityInfo
from apps.base.department.models import DepartmentInfo
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
                if isinstance(obj, TailOrder):
                    if obj.order_status > 0:
                        obj.order_status -= 1
                        obj.process_tag = 5
                        obj.save()
                        if obj.order_status == 0:
                            obj.togoods_set.all().delete()
                            _q_tail_orders = obj.ori_tail_order.tailorder_set.all().filter(order_status__in=[1, 2, 3])
                            if _q_tail_orders.exists():
                                self.message_user("%s 取消成功，但是还存在其他子订单未驳回，源订单无法被驳回" % obj.order_id, "success")
                                obj.ori_tail_order.process_tag = 7
                                obj.ori_tail_order.save()
                            else:
                                obj.ori_tail_order.order_status = 2
                                obj.ori_tail_order.process_tag = 5

                                obj.ori_tail_order.save()
                                self.message_user("%s 取消成功，并且源订单驳回到待审核状态" % obj.order_id, "success")
                        else:
                            self.message_user("%s 驳回上一级成功" % obj.order_id, "success")

                    else:
                        n -= 1
                        self.message_user("%s 单据状态错误，请检查，驳回出错。" % obj.order_id, "error")

                if isinstance(obj, PayBillOrder):
                    if obj.order_status > 0:
                        obj.order_status -= 1
                        obj.process_tag = 5
                        obj.save()
                        if obj.order_status == 0:
                            obj.pbogoods_set.all().delete()
                            obj.tail_order.order_status = 1
                            obj.tail_order.process_tag = 5
                            obj.tail_order.save()
                            self.message_user("%s 取消成功，并且源订单驳回到待审核状态" % obj.order_id, "success")
                        else:
                            self.message_user("%s 驳回上一级成功" % obj.order_id, "success")

                if isinstance(obj, FinalStatement):
                    if obj.order_status > 0:
                        obj.order_status -= 1
                        obj.process_tag = 5
                        obj.save()
                        self.message_user("%s 驳回上一级成功" % obj.order_id, "success")

                if isinstance(obj, RefundOrder):
                    if obj.process_tag in [5, 6]:
                        self.message_user("%s 已经收货无法驳回" % obj.order_id, "error")
                        n -= 1
                        continue
                    if obj.order_status > 0:
                        obj.order_status -= 1
                        obj.process_tag = 8
                        obj.rogoods_set.all().update(order_status=1)
                        if obj.order_status == 0:
                            obj.quantity = 0
                            obj.amount = 0
                            obj.rogoods_set.all().delete()
                            self.message_user("%s 取消成功，并且源订单驳回到待审核状态" % obj.order_id, "success")
                        else:
                            self.message_user("%s 驳回上一级成功" % obj.order_id, "success")
                        obj.save()
                if isinstance(obj, TailPartsOrder):
                    obj.order_status -= 1
                    obj.process_tag = 5
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


# 设置订单为重损仓发货
class SetUsedOTOAction(BaseActionView):
    action_name = "set_used_oto"
    description = "设置重损仓发货"
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
            queryset.update(process_tag=8)

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


# 设置订单为重损仓发货
class SetRetreadOTOAction(BaseActionView):
    action_name = "set_retread_oto"
    description = "设置非重损仓发货"
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
            queryset.update(process_tag=9)

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


# 设置订单为特殊情况发货
class SetRepeatedOTOAction(BaseActionView):
    action_name = "set_repeated_oto"
    description = "设置特殊订单发货"
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
            queryset.update(process_tag=10)

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


# 原始尾货单提交
class SubmitOTOAction(BaseActionView):
    action_name = "submit_oto"
    description = "提交选中的订单"
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
                    _q_repeated_order = OriTailOrder.objects.filter(sent_consignee=obj.sent_consignee,
                                                                    order_status__in=[2, 3, 4])
                    if _q_repeated_order.exists():
                        if obj.process_tag != 10:
                            self.message_user("%s 重复提交的订单" % obj.order_id, "error")
                            obj.mistake_tag = 15
                            obj.save()
                            n -= 1
                            continue
                    _q_repeated_order = OriTailOrder.objects.filter(sent_smartphone=obj.sent_smartphone,
                                                                    order_status__in=[2, 3, 4])
                    if _q_repeated_order.exists():
                        if obj.process_tag != 10:
                            self.message_user("%s 重复提交的订单" % obj.order_id, "error")
                            obj.mistake_tag = 15
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
                    if obj.process_tag != 10:
                        if obj.mode_warehouse:

                            if obj.process_tag != 8:
                                self.message_user("%s 发货仓库和单据类型不符" % obj.order_id, "error")
                                obj.mistake_tag = 12
                                obj.save()
                                n -= 1
                                continue
                        else:
                            if obj.process_tag != 9:
                                self.message_user("%s 发货仓库和单据类型不符" % obj.order_id, "error")
                                obj.mistake_tag = 12
                                obj.save()
                                n -= 1
                                continue
                    check_name = obj.goods_name()
                    if check_name not in ['无', '多种']:
                        check_name = check_name.lower().replace(' ', '')
                        if check_name not in obj.message:
                            self.message_user("%s 发货型号与备注不符" % obj.order_id, "error")
                            obj.mistake_tag = 16
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


# 设置订单为物流发货
class SetOTOAction(BaseActionView):
    action_name = "set_logistics_oto"
    description = "设置物流发货"
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


# 设置订单为正常
class SetOTONullAction(BaseActionView):
    action_name = "set_null_oto"
    description = "恢复单据标签"
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
            queryset.update(process_tag=0)

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


# 审核不用拆单原始订单
class CheckOTOAction(BaseActionView):
    action_name = "submit_single_oto"
    description = "普通审核"
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
                    _q_tail_order = TailOrder.objects.filter(order_id=obj.order_id)
                    if _q_tail_order.exists():
                        _q_update_order = _q_tail_order.filter(order_status=0)
                        if _q_update_order.exists():
                            tail_order = _q_update_order[0]
                            tail_order.order_status = 1
                        else:
                            self.message_user("%s 生成尾货订单重复，检查后处理" % obj.order_id, "error")
                            obj.mistake_tag = 9
                            obj.save()
                            n -= 1
                            continue
                    else:
                        obj.handle_time = datetime.datetime.now()
                        start_time = datetime.datetime.strptime(str(obj.submit_time).split(".")[0], "%Y-%m-%d %H:%M:%S")
                        end_time = datetime.datetime.strptime(str(obj.handle_time).split(".")[0], "%Y-%m-%d %H:%M:%S")
                        d_value = end_time - start_time
                        days_seconds = d_value.days * 3600
                        total_seconds = days_seconds + d_value.seconds
                        obj.handle_interval = math.floor(total_seconds / 60)
                    copy_fields_order = ['shop', 'order_id', 'order_category', 'sent_consignee', 'sent_smartphone',
                                         'sent_city', 'sent_district', 'sent_address', 'amount', 'mode_warehouse',
                                         'message', 'creator', 'sign_company', 'sign_department']

                    for key in copy_fields_order:
                        value = getattr(obj, key, None)
                        setattr(tail_order, key, value)

                    tail_order.sent_province = obj.sent_city.province
                    tail_order.creator = self.request.user.username
                    tail_order.ori_amount = obj.amount
                    tail_order.ori_tail_order = obj
                    tail_order.submit_time = datetime.datetime.now()
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


# 审核拆单原始订单
class SplitOTOAction(BaseActionView):
    action_name = "submit_split_oto"
    description = "拆单审核"
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

                    if obj.mistake_tag == 5:
                        _q_goods = obj.otogoods_set.all()

                        l_name, l_quantity, l_price = [goods.goods_name for goods in _q_goods], [goods.quantity for goods in _q_goods], [goods.price for goods in _q_goods]
                        groups = []
                        for i in range(len(l_name)):
                            if int(l_quantity[i]) == 1:
                                group = {l_name[i]: l_price[i]}
                                groups.append(group)
                            elif int(l_quantity[i]) > 1:
                                for j in range(int(l_quantity[i])):
                                    group = {l_name[i]: l_price[i]}
                                    groups.append(group)
                            else:
                                self.message_user("%s 货品数量错误" % obj.order_id, "error")
                                obj.mistake_tag = 8
                                obj.save()
                                n -= 1
                                continue

                        tail_quantity = len(groups)
                        for tail_num in range(tail_quantity):
                            tail_order = TailOrder()
                            series_number = tail_num + 1
                            order_id = '%s-%s' % (obj.order_id, series_number)

                            _q_tail_order = TailOrder.objects.filter(order_id=order_id)
                            if _q_tail_order.exists():
                                _q_update_order = _q_tail_order.filter(order_status=0)
                                if _q_update_order.exists():
                                    tail_order = _q_update_order[0]
                                    tail_order.order_status = 1
                                else:
                                    self.message_user("%s 生成尾货订单重复，检查后处理" % obj.order_id, "error")
                                    obj.mistake_tag = 9
                                    obj.save()
                                    n -= 1
                                    continue
                            tail_order.order_id = order_id
                            tail_order.submit_time = datetime.datetime.now()
                            tail_order.ori_tail_order = obj
                            copy_fields_order = ['shop', 'order_category', 'sent_consignee', 'sent_smartphone',
                                                 'sent_city', 'sent_district', 'sent_address', 'mode_warehouse',
                                                 'message', 'sign_company', 'sign_department']
                            for key in copy_fields_order:
                                value = getattr(obj, key, None)
                                setattr(tail_order, key, value)

                            tail_order.sent_province = obj.sent_city.province
                            tail_order.creator = self.request.user.username
                            tail_order.ori_amount = obj.amount
                            try:
                                tail_order.save()
                            except Exception as e:
                                self.message_user("%s 生成订单出错，请仔细检查 %s" % (obj.order_id, e), "error")
                                obj.mistake_tag = 10
                                obj.save()
                                n -= 1
                                continue
                            current_amount = 0
                            for goods, price in groups[tail_num].items():
                                goods_order = TOGoods()
                                goods_order.tail_order = tail_order
                                goods_order.goods_name = goods
                                goods_order.goods_nickname = goods.goods_name
                                goods_order.goods_id = goods.goods_id
                                goods_order.quantity = 1
                                goods_order.price = price
                                goods_order.amount = price
                                goods_order.settlement_price = price * obj.sign_company.discount_rate
                                goods_order.settlement_amount = price * obj.sign_company.discount_rate
                                current_amount = goods_order.amount
                                goods_order.memorandum = '来源 %s 的第 %s 个订单' % (obj.order_id, tail_num + 1)

                                try:
                                    goods_order.creator = self.request.user.username
                                    goods_order.save()
                                except Exception as e:
                                    self.message_user("%s 生成订单货品出错，请仔细检查 %s" % (obj.order_id, e), "error")
                                    obj.mistake_tag = 11
                                    obj.save()
                                    n -= 1
                                    continue

                            tail_order.amount = current_amount
                            tail_order.quantity = 1
                            tail_order.save()

                        obj.handle_time = datetime.datetime.now()
                        start_time = datetime.datetime.strptime(str(obj.submit_time).split(".")[0],
                                                                "%Y-%m-%d %H:%M:%S")
                        end_time = datetime.datetime.strptime(str(obj.handle_time).split(".")[0],
                                                              "%Y-%m-%d %H:%M:%S")
                        d_value = end_time - start_time
                        days_seconds = d_value.days * 3600
                        total_seconds = days_seconds + d_value.seconds
                        obj.handle_interval = math.floor(total_seconds / 60)
                        obj.order_status = 3
                        obj.mistake_tag = 0
                        obj.process_tag = 6
                        obj.save()

                    else:
                        self.message_user("%s 为标记拆分订单，请先用普通模式审核。" % obj.order_id, "error")
                        obj.mistake_tag = 0
                        obj.save()
                        n -= 1
                        continue

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


# 审核尾货订单
class CheckTOAction(BaseActionView):
    action_name = "submit_to"
    description = "审核选中的订单"
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
                    if not obj.track_no:
                        self.message_user("%s 物流追踪信息错误" % obj.order_id, "error")
                        obj.mistake_tag = 1
                        obj.save()
                        n -= 1
                        continue
                    if int(len(obj.track_no)) < 7:
                        self.message_user("%s 物流追踪信息错误" % obj.order_id, "error")
                        obj.mistake_tag = 1
                        obj.save()
                        n -= 1
                        continue

                    bill_order = PayBillOrder()
                    _q_bill_order = PayBillOrder.objects.filter(order_id=obj.order_id)
                    if _q_bill_order.exists():
                        _q_update_order = _q_bill_order.filter(order_status=0)
                        if _q_update_order.exists():
                            bill_order = _q_update_order[0]
                            bill_order.order_status = 1
                        else:
                            self.message_user("%s 生成尾货订单重复，检查后处理" % obj.order_id, "error")
                            obj.mistake_tag = 2
                            obj.save()
                            n -= 1
                            continue
                    else:
                        obj.handle_time = datetime.datetime.now()
                        start_time = datetime.datetime.strptime(str(obj.submit_time).split(".")[0],
                                                                "%Y-%m-%d %H:%M:%S")
                        end_time = datetime.datetime.strptime(str(obj.handle_time).split(".")[0],
                                                              "%Y-%m-%d %H:%M:%S")
                        d_value = end_time - start_time
                        days_seconds = d_value.days * 3600
                        total_seconds = days_seconds + d_value.seconds
                        obj.handle_interval = math.floor(total_seconds / 60)
                    copy_fields_order = ['shop', 'order_id', 'order_category', 'sent_consignee', 'sent_smartphone',
                                         'quantity', 'amount', 'mode_warehouse', 'creator', 'sign_company',
                                         'sign_department']

                    for key in copy_fields_order:
                        value = getattr(obj, key, None)
                        setattr(bill_order, key, value)
                    bill_order.message = obj.message[:199]
                    bill_order.creator = self.request.user.username
                    bill_order.submit_time = datetime.datetime.now()
                    bill_order.tail_order = obj
                    try:
                        bill_order.save()
                    except Exception as e:
                        self.message_user("%s 生成结算单出错 %s" % (obj.order_id, e), "error")
                        obj.mistake_tag = 3
                        obj.save()
                        n -= 1
                        continue
                    _q_goods = obj.togoods_set.all()
                    for good in _q_goods:
                        pbo_good = PBOGoods()
                        pbo_good.pb_order = bill_order
                        pbo_good.goods_nickname = good.goods_name.goods_name
                        copy_fields_goods = ['goods_id', 'goods_name', 'quantity', 'settlement_price',
                                             'settlement_amount', 'settlement_amount', 'memorandum', 'creator']
                        for key in copy_fields_goods:
                            value = getattr(good, key, None)
                            setattr(pbo_good, key, value)
                        try:
                            pbo_good.save()
                        except Exception as e:
                            self.message_user("%s 生成结算单货品出错 %s" % (obj.order_id, e), "error")
                            obj.mistake_tag = 4
                            obj.save()
                            continue

                    obj.order_status = 2
                    obj.mistake_tag = 0
                    obj.process_tag = 4

                    obj.save()

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


# 提交尾货结算单
class SubmitPBOAction(BaseActionView):
    action_name = "submit_pbo"
    description = "审核选中的结算单"
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
                queryset.update(order_status=2)

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


# 确认尾货结算单
class SetPBOAction(BaseActionView):
    action_name = "set_pbo"
    description = "设置单据为已确认"
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
            queryset.update(message='确认可付款 %s' % self.request.user.username)
            queryset.update(process_tag=2)

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


# 清空标记尾货结算单
class SetPBOCAction(BaseActionView):
    action_name = "set_pbo_clear"
    description = "清除已确认单据标记"
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
            queryset.update(process_tag=0)

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


# 审核尾货结算单
class CheckPBOAction(BaseActionView):
    action_name = "check_pbo"
    description = "审核选中的结算单"
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
                queryset.update(order_status=3)
            else:
                for obj in queryset:
                    if obj.process_tag != 2:
                        self.message_user("%s 此单还没有确认" % obj.order_id, "error")
                        obj.mistake_tag = 4
                        obj.save()
                        n -= 1
                        continue
                    self.log('change', '', obj)
                    i = 1
                    goods_orders = obj.pbogoods_set.all()
                    for goods_order in goods_orders:
                        _q_pbo2acc_order = PBillToAccount.objects.filter(pbo_order=goods_order)
                        if _q_pbo2acc_order.exists():
                            self.message_user("%s 重复生成结算单，联系管理员" % goods_order, "error")
                            obj.mistake_tag = 3
                            obj.save()
                            n -= 1
                            continue
                        acc_order = AccountInfo()
                        _q_acc_order = PBillToAccount.objects.filter(pbo_order=goods_order)
                        if _q_acc_order.exists():
                            _check_acc_order = _q_acc_order[0].account_order
                            if _check_acc_order.order_status == 0:
                                acc_order = _check_acc_order
                                acc_order.order_status = 1
                            else:
                                self.message_user("%s 生成尾货结算重复，检查后处理" % obj.order_id, "error")
                                obj.mistake_tag = 1
                                obj.save()
                                n -= 1
                                continue
                        copy_fields_order = ['shop', 'order_category', 'mode_warehouse', 'sent_consignee',
                                             'sign_company', 'sign_department', 'sent_smartphone', 'message']

                        for key in copy_fields_order:
                            value = getattr(obj, key, None)
                            setattr(acc_order, key, value)

                        copy_fields_goods = ['goods_id', 'goods_name', 'goods_nickname', 'quantity',
                                             'settlement_price', 'settlement_amount']

                        for key in copy_fields_goods:
                            value = getattr(goods_order, key, None)
                            setattr(acc_order, key, value)

                        acc_order.creator = self.request.user.username
                        acc_order.order_id = "%s-%s-%s" % (obj.order_id, i, goods_order.goods_id)
                        i += 1
                        acc_order.submit_time = datetime.datetime.now()
                        pb2acc_order = PBillToAccount()
                        pb2acc_order.pbo_order = goods_order
                        try:
                            acc_order.save()
                            pb2acc_order.account_order = acc_order
                            pb2acc_order.save()
                        except Exception as e:
                            self.message_user("%s 生成结算单出错 %s" % (obj.order_id, e), "error")
                            obj.mistake_tag = 2
                            obj.save()
                            n -= 1
                            continue

                    if not obj.handle_time:
                        obj.handle_time = datetime.datetime.now()
                        start_time = datetime.datetime.strptime(str(obj.submit_time).split(".")[0],
                                                                "%Y-%m-%d %H:%M:%S")
                        end_time = datetime.datetime.strptime(str(obj.handle_time).split(".")[0],
                                                              "%Y-%m-%d %H:%M:%S")
                        d_value = end_time - start_time
                        days_seconds = d_value.days * 3600
                        total_seconds = days_seconds + d_value.seconds
                        obj.handle_interval = math.floor(total_seconds / 60)

                    obj.order_status = 3
                    obj.mistake_tag = 0
                    obj.process_tag = 4

                    obj.save()

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


# 批量汇总生成付款单
class CheckACCAction(BaseActionView):
    action_name = "submit_acc"
    description = "批量汇总生成收款单"
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
                if queryset.filter(mistake_tag=2).exists():
                    self.message_user("汇总账单明细货品错误, 不允许重复递交，联系管理员处理", "error")
                    n = 0
                    self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                                      'success')
                    return None
                check_n = queryset.filter(final_statement__isnull=True).count()
                if check_n != n:
                    self.message_user("汇总账单明细中存在已有账单的情况, 不允许重复递交，请选择未递交过的明细单", "error")

                    n = 0
                    self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                                      'success')
                    return None
                fs_order = FinalStatement()
                i = 1
                while True:
                    sn = 1000 + int(i)
                    prefix = "FS"
                    serial_number = str(datetime.datetime.now())
                    serial_number = serial_number.replace("-", "")[:6]
                    order_id = prefix + str(serial_number) + str(sn)[-3:]
                    _q_fs_order = FinalStatement.objects.filter(order_id=order_id)
                    if _q_fs_order.exists():
                        i += 1
                    else:
                        fs_order.order_id = order_id
                        break
                fs_order.mode_warehouse = queryset[0].mode_warehouse
                fs_order.sign_company = queryset[0].sign_company
                fs_order.sign_department = queryset[0].sign_department
                fs_order.shop = queryset[0].shop
                if fs_order.mode_warehouse:
                    fs_order.payee = '北京中芯线科技有限公司'
                    fs_order.bank = '中国建设银行北京润德支行'
                    fs_order.account = '11001093901052510298'
                else:
                    fs_order.payee = '陈岩'
                    fs_order.bank = '中国工商银行武汉百瑞景支行'
                    fs_order.account = '6215593202020467216'
                fs_order.amount = queryset.aggregate(amount=Sum('settlement_amount'))["amount"]
                fs_order.quantity = queryset.aggregate(quantity=Sum('quantity'))['quantity']
                fs_order.submit_time = datetime.datetime.now()
                try:
                    fs_order.creator = self.request.user.username
                    fs_order.save()
                    queryset.update(final_statement=fs_order)
                except Exception as e:
                    self.message_user("汇总账单明细出错，%s, 请仔细检查" % e, "error")
                    queryset.update(mistake_tag=1)
                    n = 0
                    self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                                      'success')
                    return None

                goods_groups = [{obj.goods_name: [obj.quantity, obj.settlement_price, obj.settlement_amount, obj.order_category]} for obj in queryset]
                for good_info in goods_groups:
                    for goods, info in good_info.items():
                        goods_order = FinalStatementGoods()
                        goods_order.fs_order = fs_order

                        goods_order.goods_name = goods
                        goods_order.goods_id = goods.goods_id
                        goods_order.goods_nickname = goods.goods_name
                        goods_order.quantity = info[0]
                        goods_order.settlement_price = info[1]
                        goods_order.settlement_amount = info[2]
                        goods_order.order_category = info[3]
                        goods_order.creator = self.request.user.username
                        try:
                            goods_order.save()
                        except Exception as e:
                            self.message_user("汇总账单明细货品出错，%s, 请截图至管理员" % e, "error")
                            queryset.update(mistake_tag=2)
                            n = 0
                            self.message_user(
                                "成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                                'success')
                            return None
                for obj in queryset:
                    obj.handle_time = datetime.datetime.now()
                    start_time = datetime.datetime.strptime(str(obj.submit_time).split(".")[0],
                                                            "%Y-%m-%d %H:%M:%S")
                    end_time = datetime.datetime.strptime(str(obj.handle_time).split(".")[0],
                                                          "%Y-%m-%d %H:%M:%S")
                    d_value = end_time - start_time
                    days_seconds = d_value.days * 3600
                    total_seconds = days_seconds + d_value.seconds
                    obj.handle_interval = math.floor(total_seconds / 60)
                    obj.process_tag = 4
                    obj.order_status = 2
                    obj.save()

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


# 确认付款账单
class AffirmFSAction(BaseActionView):
    action_name = "affirm_fs"
    description = "确认收款账单"
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
                    obj.submit_time = datetime.datetime.now()
                    obj.save()

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


# 提交付款账单
class SubmitFSAction(BaseActionView):
    action_name = "submit_fs"
    description = "提交已付款账单"
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
                    if not obj.pay_order_id:
                        self.message_user("%s 此单还没有付款单号" % obj.order_id, "error")
                        obj.mistake_tag = 1
                        obj.save()
                        n -= 1
                        continue

                    obj.handle_time = datetime.datetime.now()
                    start_time = datetime.datetime.strptime(str(obj.submit_time).split(".")[0],
                                                            "%Y-%m-%d %H:%M:%S")
                    end_time = datetime.datetime.strptime(str(obj.handle_time).split(".")[0],
                                                          "%Y-%m-%d %H:%M:%S")
                    d_value = end_time - start_time
                    days_seconds = d_value.days * 3600
                    total_seconds = days_seconds + d_value.seconds
                    obj.handle_interval = math.floor(total_seconds / 60)

                    obj.order_status = 3
                    obj.mistake_tag = 0
                    obj.save()

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


# 确认付款单
class SetFSAction(BaseActionView):
    action_name = "set_fs"
    description = "设置单据为已确认"
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
            queryset.update(feedback='已确认收款 %s' % self.request.user.username)
            queryset.update(process_tag=2)

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


# 审核付款账单完结付款明细
class CheckFSAction(BaseActionView):
    action_name = "submit_fs"
    description = "提交已付款账单"
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
                    if not obj.feedback or obj.process_tag != 2:
                        self.message_user("%s 此单还没有确认" % obj.order_id, "error")
                        obj.mistake_tag = 1
                        obj.save()
                        n -= 1
                        continue
                    obj.accountinfo_set.all().update(order_status=3)
                    obj.order_status = 4
                    obj.mistake_tag = 0
                    obj.save()

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


# 标记为货到付款
class SetROEAction(BaseActionView):
    action_name = "set_ro_exchange"
    description = "设置单据为换货单"
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
            queryset.update(process_tag=7)

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


# 清除标记
class SetROCAction(BaseActionView):
    action_name = "set_ro_clear"
    description = "清除标记设置"
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
            queryset.update(process_tag=0)

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


# 提交退换单
class SubimtROAction(BaseActionView):
    action_name = "submit_ro"
    description = "提交退换单"
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
                    if obj.tail_order.order_status != 2:
                        self.message_user("%s 关联的发货单还未发货" % obj.order_id, "error")
                        obj.mistake_tag = 13
                        obj.save()
                        n -= 1
                        continue
                    if obj.order_category != 3:
                        self.message_user("%s 现阶段只支持退货单，更正为退货单" % obj.order_id, "error")
                        obj.mistake_tag = 14
                        obj.save()
                        n -= 1
                        continue
                    if obj.order_id:
                        _q_refund_quantity = obj.tail_order.refund_tail_order.all().filter(
                            order_status__in=[1, 2, 3]).aggregate(quantity=Sum('quantity'))['quantity']
                        if _q_refund_quantity > obj.tail_order.quantity:
                            self.message_user("%s 同一发货单不允许重复创建退款单" % obj.order_id, "error")
                            obj.mistake_tag = 1
                            obj.save()
                            n -= 1
                            continue
                        _q_refund_amount = obj.tail_order.refund_tail_order.all().filter(
                            order_status__in=[1, 2, 3]).aggregate(amount=Sum('amount'))['amount']
                        if _q_refund_amount > obj.tail_order.amount:
                            self.message_user("%s 同一发货单不允许重复创建退款单" % obj.order_id, "error")
                            obj.mistake_tag = 2
                            obj.save()
                            n -= 1
                            continue
                    if not obj.info_refund:
                        self.message_user("%s 此单还没有退换原因" % obj.order_id, "error")
                        obj.mistake_tag = 3
                        obj.save()
                        n -= 1
                        continue
                    if not obj.track_no:
                        self.message_user("%s 此单还没有退回单号" % obj.order_id, "error")
                        obj.mistake_tag = 4
                        obj.save()
                        n -= 1
                        continue
                    if obj.order_category == 4:
                        if obj.process_tag != 7:
                            self.message_user("%s 换货单必须要进行标记" % obj.order_id, "error")
                            obj.mistake_tag = 5
                            obj.save()
                            n -= 1
                            continue
                    if obj.process_tag == 7:
                        if obj.order_category != 4:
                            self.message_user("%s 非换货单不可以标记换货" % obj.order_id, "error")
                            obj.mistake_tag = 6
                            obj.save()
                            n -= 1
                            continue
                    obj.submit_time = datetime.datetime.now()
                    obj.order_status = 2
                    obj.process_tag = 0
                    obj.rogoods_set.all().update(order_status=2)
                    obj.mistake_tag = 0
                    obj.save()

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


# 设置待入库处理标记
class SetROGHAction(BaseActionView):
    action_name = "set_rog_handle"
    description = "设置待处理标记"
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
            queryset.update(process_tag=2)

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


# 设置待入库处理标记
class SetROGCAction(BaseActionView):
    action_name = "set_rog_clear"
    description = "清除标记设置"
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
            queryset.update(process_tag=0)

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


# 提交入库单
class StockROGAction(BaseActionView):
    action_name = "stock_ro_goods"
    description = "提交入库单"
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
                    if obj.receipted_quantity:
                        if obj.quantity != obj.receipted_quantity:
                            if obj.quantity > obj.receipted_quantity:
                                self.message_user("%s 入库数量小于待收货量" % obj, "error")
                                obj.mistake_tag = 2
                                obj.order_status = 3
                                obj.save()
                                n -= 1
                                continue
                            else:
                                self.message_user("%s 入库数量不等于待收货量" % obj, "error")
                                obj.mistake_tag = 2
                                obj.save()
                                n -= 1
                                continue
                    else:
                        self.message_user("%s 无入库数量" % obj, "error")
                        obj.mistake_tag = 1
                        obj.save()
                        n -= 1
                        continue
                    obj.order_status = 4
                    obj.process_tag = 4
                    obj.mistake_tag = 0
                    obj.save()

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


# 设置退换单
class SetROAction(BaseActionView):
    action_name = "set_ro"
    description = "设置单据为已建单"
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
            queryset.update(message='确认可付款 %s' % self.request.user.username)
            queryset.update(process_tag=4)

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


# 审核退换单
class CheckROAction(BaseActionView):
    action_name = "check_ro"
    description = "审核退换单"
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
                    if obj.process_tag != 6:
                        self.message_user("%s 非已到货状态不可以审核" % obj.order_id, "error")
                        obj.mistake_tag = 7
                        obj.save()
                        n -= 1
                        continue
                    if obj.quantity != obj.receipted_quantity:
                        self.message_user("%s 退换数量和收货数量不一致" % obj.order_id, "error")
                        obj.mistake_tag = 8
                        obj.save()
                        n -= 1
                        continue
                    if obj.quantity != obj.receipted_quantity:
                        self.message_user("%s 退换金额和收货金额不一致" % obj.order_id, "error")
                        obj.mistake_tag = 9
                        obj.save()
                        n -= 1
                        continue

                    arrears_order = ArrearsBillOrder()
                    _q_arrears_order = ArrearsBillOrder.objects.filter(order_id=obj.order_id)
                    if _q_arrears_order.exists():
                        _q_update_order = _q_arrears_order.filter(order_status=0)
                        if _q_update_order.exists():
                            arrears_order = _q_update_order[0]
                            arrears_order.order_status = 1
                        else:
                            self.message_user("%s 生成退换结算单重复，检查后处理" % obj.order_id, "error")
                            obj.mistake_tag = 10
                            obj.save()
                            n -= 1
                            continue
                    else:
                        obj.handle_time = datetime.datetime.now()
                        start_time = datetime.datetime.strptime(str(obj.submit_time).split(".")[0],
                                                                "%Y-%m-%d %H:%M:%S")
                        end_time = datetime.datetime.strptime(str(obj.handle_time).split(".")[0],
                                                              "%Y-%m-%d %H:%M:%S")
                        d_value = end_time - start_time
                        days_seconds = d_value.days * 3600
                        total_seconds = days_seconds + d_value.seconds
                        obj.handle_interval = math.floor(total_seconds / 60)
                    copy_fields_order = ['shop', 'order_id', 'order_category', 'sent_consignee', 'sent_smartphone',
                                         'mode_warehouse', 'creator', 'sign_company', 'message', 'sign_department']

                    for key in copy_fields_order:
                        value = getattr(obj, key, None)
                        setattr(arrears_order, key, value)

                    arrears_order.creator = self.request.user.username
                    arrears_order.settlement_quantity = -obj.receipted_quantity
                    arrears_order.settlement_amount = -obj.receipted_amount
                    arrears_order.submit_time = datetime.datetime.now()
                    arrears_order.refund_order = obj
                    try:
                        arrears_order.save()
                    except Exception as e:
                        self.message_user("%s 生成结算单出错 %s" % (obj.order_id, e), "error")
                        obj.mistake_tag = 11
                        obj.save()
                        n -= 1
                        continue
                    _q_goods = obj.rogoods_set.all()
                    goods_error = 0
                    for good in _q_goods:
                        abo_good = ABOGoods()
                        abo_good.ab_order = arrears_order
                        abo_good.goods_nickname = good.goods_name.goods_name
                        abo_good.settlement_quantity = -good.receipted_quantity
                        abo_good.settlement_amount = -good.settlement_amount
                        copy_fields_goods = ['goods_id', 'goods_name', 'settlement_price', 'memorandum']
                        for key in copy_fields_goods:
                            value = getattr(good, key, None)
                            setattr(abo_good, key, value)
                        try:
                            abo_good.save()
                        except Exception as e:
                            self.message_user("%s 生成结算单货品出错 %s" % (obj.order_id, e), "error")
                            obj.mistake_tag = 12
                            goods_error = 1
                            obj.save()
                            continue
                    if goods_error:
                        continue
                    obj.order_status = 3
                    obj.mistake_tag = 0
                    obj.process_tag = 4

                    obj.save()

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')


# 审核退换结算单
class CheckAOAction(BaseActionView):
    action_name = "check_ao"
    description = "审核退换结算单"
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
                    if obj.process_tag != 2:
                        self.message_user("%s 此单还没有确认" % obj.order_id, "error")
                        obj.mistake_tag = 4
                        obj.save()
                        n -= 1
                        continue
                    self.log('change', '', obj)
                    goods_orders = obj.abogoods_set.all()
                    i = 1
                    error_tag = 0
                    for goods_order in goods_orders:
                        _q_abo2acc_order = ABillToAccount.objects.filter(abo_order=goods_order)
                        if _q_abo2acc_order.exists():
                            self.message_user("%s 重复生成结算单，联系管理员" % goods_order, "error")
                            obj.mistake_tag = 3
                            obj.save()
                            n -= 1
                            continue
                        acc_order = AccountInfo()
                        _q_acc_order = ABillToAccount.objects.filter(abo_order=goods_order)
                        if _q_acc_order.exists():
                            _check_acc_order = _q_acc_order[0].account_order
                            if _check_acc_order.order_status == 0:
                                acc_order = _check_acc_order
                                acc_order.order_status = 1
                            else:
                                self.message_user("%s 生成尾货结算重复，检查后处理" % obj.order_id, "error")
                                obj.mistake_tag = 1
                                obj.save()
                                n -= 1
                                continue
                        copy_fields_order = ['shop', 'order_category', 'mode_warehouse', 'sent_consignee',
                                             'sign_company', 'sign_department', 'sent_smartphone', 'message']

                        for key in copy_fields_order:
                            value = getattr(obj, key, None)
                            setattr(acc_order, key, value)

                        copy_fields_goods = ['goods_id', 'goods_name', 'goods_nickname',
                                             'settlement_price', 'settlement_amount']

                        for key in copy_fields_goods:
                            value = getattr(goods_order, key, None)
                            setattr(acc_order, key, value)
                        acc_order.quantity = goods_order.settlement_quantity

                        acc_order.creator = self.request.user.username
                        acc_order.order_id = "%s-%s-%s" % (obj.order_id, i, goods_order.goods_id)
                        i += 1
                        acc_order.submit_time = datetime.datetime.now()
                        ab2acc_order = ABillToAccount()
                        ab2acc_order.abo_order = goods_order
                        try:
                            acc_order.save()
                            ab2acc_order.account_order = acc_order
                            ab2acc_order.save()
                        except Exception as e:
                            self.message_user("%s 生成结算单出错 %s" % (obj.order_id, e), "error")
                            obj.mistake_tag = 2
                            obj.save()
                            n -= 1
                            error_tag = 1
                            continue
                    if error_tag:
                        continue
                    if not obj.handle_time:
                        obj.handle_time = datetime.datetime.now()
                        start_time = datetime.datetime.strptime(str(obj.submit_time).split(".")[0],
                                                                "%Y-%m-%d %H:%M:%S")
                        end_time = datetime.datetime.strptime(str(obj.handle_time).split(".")[0],
                                                              "%Y-%m-%d %H:%M:%S")
                        d_value = end_time - start_time
                        days_seconds = d_value.days * 3600
                        total_seconds = days_seconds + d_value.seconds
                        obj.handle_interval = math.floor(total_seconds / 60)

                    obj.order_status = 2
                    obj.mistake_tag = 0
                    obj.process_tag = 4
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
    list_display = ['shop',  'mistake_tag', 'goods_name', 'quantity', 'amount', 'sent_consignee', 'sent_smartphone', 'sent_address',
                    'message', 'order_id', 'feedback', 'process_tag', 'mode_warehouse', 'order_category',
                    'order_status', 'sent_city', 'sent_district',   'sign_company', 'sign_department', ]
    actions = [SetUsedOTOAction, SetRetreadOTOAction, SetRepeatedOTOAction, SubmitOTOAction, RejectSelectedAction]

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

            self.message_user('结果提示：%s' % result)
        return super(OTOUnhandleAdmin, self).post(request, *args, **kwargs)

    def handle_upload_file(self, _file):
        INIT_FIELDS_DIC = {
            '店铺': 'shop',
            '源单号': 'order_id',
            '订单类型': 'order_category',
            '发货模式': 'mode_warehouse',
            '收件人姓名': 'sent_consignee',
            '收件人手机': 'sent_smartphone',
            '收件城市': 'sent_city',
            '收件区县': 'sent_district',
            '收件地址': 'sent_address',
            '订单留言': 'message',
            '订单反馈': 'feedback',
            '货品编码': 'goods_id',
            '数量': 'quantity',
            '单价': 'price',
        }
        ALLOWED_EXTENSIONS = ['xls', 'xlsx']
        report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error": []}

        if '.' in _file.name and _file.name.rsplit('.')[-1] in ALLOWED_EXTENSIONS:
            with pd.ExcelFile(_file) as xls:
                df = pd.read_excel(xls, sheet_name=0, converters={u'货品编码': str})
                FILTER_FIELDS = ['店铺', '源单号', '订单类型', '发货模式', '收件人姓名', '收件人手机', '收件城市',
                                 '收件区县', '收件地址', '订单留言', '货品编码', '数量', '单价']

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
                check_list = ['shop', 'order_id', 'order_category', 'mode_warehouse', 'sent_consignee',
                              'sent_smartphone', 'sent_city', 'sent_district', 'sent_address',
                              'message', 'goods_id']
                df_check = df[check_list]

                order_ids = list(set(df_check.order_id))
                for order_id in order_ids:
                    check_info_list = ['shop', 'order_id', 'order_category', 'mode_warehouse', 'sent_consignee',
                                       'sent_smartphone', 'sent_city', 'sent_district', 'sent_address', 'message']
                    data_check = df_check[df_check.order_id == order_id]
                    if len(data_check.goods_id) != len(list(set(data_check.goods_id))):
                        error = '单号%s，货品重复，请剔除重复货品' % str(order_id)
                        report_dic["error"].append(error)
                        return report_dic
                    for word in check_info_list:
                        check_word = data_check[word]
                        if np.any(check_word.isnull() == True):
                            continue
                        check_word = list(set(check_word))
                        if len(check_word) > 1:
                            error = '单号%s的%s不一致，相同单号%s必须相同' % (str(order_id), str(word), str(word))
                            report_dic["error"].append(error)
                            return report_dic

                # 获取导入表格的字典，每一行一个字典。这个字典最后显示是个list
                for order_id in order_ids:
                    df_invoice = df[df.order_id == order_id]
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

        ori_tail_order = OriTailOrder()

        if not re.match(r'^[0-9A-Z]+$', resource[0]['order_id']):
            error = '源单号%s非法，请使用正确的源单号格式（只支持英文字母和数字组合）' % resource[0]['order_id']
            report_dic['error'].append(error)
            return report_dic
        else:
            ori_tail_order.order_id = resource[0]['order_id']

        _q_work_order = OriTailOrder.objects.filter(order_id=resource[0]['order_id'])
        if not _q_work_order.exists():
            # 开始导入数据
            check_list = ['order_id','sent_consignee', 'sent_smartphone', 'sent_district', 'sent_address', 'message']

            _q_shop = ShopInfo.objects.filter(shop_name=resource[0]['shop'])
            if _q_shop.exists():
                ori_tail_order.shop = _q_shop[0]
            else:
                error = '店铺%s不存在，请使用正确的店铺名' % resource[0]['shop']
                report_dic['error'].append(error)
                return report_dic
            category = {
                '销售订单': 1,
            }
            order_category = category.get(resource[0]['order_category'], None)
            if order_category:
                ori_tail_order.order_category = order_category

            else:
                error = '订单类型%s不存在，请使用正确的订单类型' % resource[0]['order_category']
                report_dic['error'].append(error)
                return report_dic

            _q_city = CityInfo.objects.filter(city=resource[0]['sent_city'])
            if _q_city.exists():
                ori_tail_order.sent_city = _q_city[0]
            else:
                error = '城市%s非法，请使用正确的二级城市名称' % resource[0]['sent_city']
                report_dic['error'].append(error)
                return report_dic

            mode_decision = {
                '回流': 0,
                '二手': 1,
            }
            mode_warehouse = mode_decision.get(resource[0]['mode_warehouse'], None)
            if mode_warehouse is None:
                error = '二手或者回流字段：%s非法（只可以填二手或者回流）' % resource[0]['mode_warehouse']
                report_dic['error'].append(error)
                return report_dic
            else:
                ori_tail_order.mode_warehouse = mode_warehouse

            if self.request.user.company:
                ori_tail_order.sign_company = self.request.user.company
            else:
                error = '账号公司未设置或非法，联系管理员处理'
                report_dic['error'].append(error)
                return report_dic

            if self.request.user.department:
                ori_tail_order.sign_department = self.request.user.department
            else:
                error = '账号部门未设置或非法，联系管理员处理'
                report_dic['error'].append(error)
                return report_dic

            for attr in check_list:
                if resource[0][attr]:
                    setattr(ori_tail_order, attr, resource[0][attr])

            try:
                ori_tail_order.creator = self.request.user.username
                ori_tail_order.save()
                report_dic["successful"] += 1
            # 保存出错，直接错误条数计数加一。
            except Exception as e:
                report_dic["error"].append(e)
                report_dic["false"] += 1
                return report_dic
        else:
            ori_tail_order = _q_work_order[0]
            if ori_tail_order.order_status != 1:
                error = '此订单%s已经存在，请核实再导入' % (ori_tail_order.order_id)
                report_dic["error"].append(error)
                report_dic["false"] += 1
                return report_dic
            all_goods_info = ori_tail_order.otogoods_set.all()
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
                goods_order.ori_tail_order = ori_tail_order
                goods_order.creator = self.request.user.username
                try:
                    goods_order.save()
                # 保存出错，直接错误条数计数加一。
                except Exception as e:
                    report_dic["error"].append(e)
                    report_dic["false"] += 1
                    ori_tail_order.mistake_tag = 13
                    ori_tail_order.save()
                    return report_dic
            else:
                error = '尾货订单的货品编码错误，请处理好编码再导入'
                report_dic["error"].append(error)
                report_dic["false"] += 1
                ori_tail_order.mistake_tag = 14
                ori_tail_order.save()
                return report_dic

        return report_dic

    form_layout = [
        Fieldset('基本信息',
                 'shop', 'order_id', 'mode_warehouse', ),
        Fieldset('发货相关信息',
                 Row('sent_consignee', 'sent_smartphone'),
                 Row('sent_city', 'sent_district'),
                 'sent_address'),
        Fieldset(None,
                 'submit_time', 'handle_time', 'handle_interval', 'feedback', 'process_tag', 'amount', 'quantity',
                 'mistake_tag', 'order_status', 'is_delete', 'creator', 'sign_company', 'sign_department',
                 'order_category', **{"style": "display:None"}),
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
                quantity = obj.otogoods_set.all().aggregate(quantity=Sum('quantity'))['quantity']
            except Exception as e:
                amount = 0
            if amount is None:
                amount = 0
            if quantity is None:
                quantity = 0
            obj.amount = amount
            obj.quantity = quantity
            obj.save()
        return queryset


class OTOCheckAdmin(object):
    list_display = ['shop', 'order_id', 'mistake_tag', 'process_tag', 'amount', 'goods_name', 'quantity', 'order_category',
                    'mode_warehouse', 'feedback', 'sent_consignee', 'sent_smartphone', 'sent_city', 'sent_district',
                    'sent_address', 'submit_time', 'handle_time', 'handle_interval', 'message',  'sign_company',
                    'sign_department']

    actions = [SetOTONullAction, SetOTOAction, CheckOTOAction, SplitOTOAction, RejectSelectedAction,]

    search_fields = ['order_id']
    list_filter = ['mode_warehouse', 'process_tag', 'creator', 'mistake_tag', 'order_category', 'sent_smartphone',
                   'submit_time', 'create_time']

    list_editable = ['feedback']
    readonly_fields = ['shop', 'sign_company', 'order_id', 'sent_city', 'sent_district', 'sent_address', 'message',
                       'sent_consignee', 'order_category', 'sent_smartphone', 'mode_warehouse',]

    inlines = [OTOGoodsInline]

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
                 'submit_time', 'handle_time', 'handle_interval', 'process_tag', 'amount', 'quantity',
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
    list_display = ['shop', 'order_id', 'goods_name', 'quantity', 'amount', 'order_category', 'mode_warehouse',
                    'feedback', 'sent_consignee', 'sent_smartphone', 'sent_city', 'sent_district', 'sent_address',
                    'submit_time', 'handle_time', 'handle_interval', 'message',  'sign_company', 'sign_department',
                    'process_tag', 'mistake_tag', 'order_status']

    search_fields = ['order_id']
    list_filter = ['process_tag', 'mode_warehouse', 'creator', 'sent_smartphone', 'mistake_tag', 'order_category',
                   'create_time', 'submit_time', 'sign_company__company_name', ]

    readonly_fields = ['shop', 'order_id', 'amount', 'order_category', 'mode_warehouse', 'feedback', 'sent_consignee',
                       'sent_smartphone', 'sent_city', 'sent_district', 'sent_address', 'submit_time', 'handle_time',
                       'handle_interval', 'message',  'sign_company', 'sign_department', 'process_tag', 'mistake_tag',
                       'order_status']

    inlines = [OTOGoodsInline]

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
    exclude = ['creator', 'goods_id', 'is_delete', 'order_id', 'price', 'amount', 'settlement_price', 'settlement_amount']

    extra = 1
    style = 'table'


class TOhandleAdmin(object):
    list_display = ['shop', 'order_id', 'ori_tail_order', 'quantity', 'process_tag', 'mistake_tag',
                    'track_no', 'sent_consignee', 'sent_smartphone', 'sent_city', 'sent_district', 'sent_address',
                    'submit_time', 'handle_time', 'handle_interval', 'message',  'sign_company', 'sign_department',
                    'order_category', 'mode_warehouse', 'order_status']

    list_exclude = ['amount', 'ori_amount',]

    actions = [CheckTOAction, RejectSelectedAction,]

    search_fields = ['order_id']
    list_filter = ['order_id', 'mode_warehouse', 'process_tag', 'creator', 'mistake_tag', 'order_category', 'sent_smartphone',
                   'submit_time', 'create_time']

    list_editable = ['track_no']
    readonly_fields = ['shop', 'sign_company', 'order_id', 'sent_city', 'sent_district', 'sent_address', 'message',
                       'sent_consignee', 'order_category', 'sent_smartphone', 'mode_warehouse', 'feedback',
                       'ori_tail_order', 'sent_province', 'quantity', 'ori_amount', 'amount']

    inlines = [TOGoodsInline]
    ALLOWED_EXTENSIONS = ['xls', 'xlsx']
    INIT_FIELDS_DIC = {"尾货订单": "order_id", "快递信息": "track_no"}
    import_data = True

    form_layout = [
        Fieldset('驳回信息',
                 'feedback', ),
        Fieldset('基本信息',
                 Row('shop', 'sign_company'),
                 Row('order_id', 'ori_tail_order',),
                 Row('order_category', 'message',),
                 Row('mode_warehouse', 'quantity',),),
        Fieldset('单号反馈信息',
                 'track_no', ),
        Fieldset('发货相关信息',
                 Row('sent_consignee', 'sent_smartphone'),
                 Row('sent_province', 'sent_city', 'sent_district'),
                 'sent_address'),
        Fieldset(None,
                 'submit_time', 'handle_time', 'handle_interval', 'process_tag', 'feedback', 'amount', 'ori_amount',
                 'mistake_tag', 'order_status', 'is_delete', 'creator', 'sign_company', 'sign_department',
                 **{"style": "display:None"}),
    ]

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file', None)
        if file:
            result = self.handle_upload_file(request, file)
            self.message_user('导入成功数据%s条' % int(result['successful']), 'success')
            if result['false'] > 0 or result['error']:
                self.message_user('导入失败数据%s条,主要的错误是%s' % (int(result['false']), result['error']), 'warning')
            if result['repeated'] > 0:
                self.message_user('包含更新重复数据%s条' % int(result['repeated']), 'error')
        return super(TOhandleAdmin, self).post(request, *args, **kwargs)

    def handle_upload_file(self, request, _file):
        report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error": []}
        if '.' in _file.name and _file.name.rsplit('.')[-1] in self.__class__.ALLOWED_EXTENSIONS:
            df = pd.read_excel(_file, sheet_name=0, converters={u'原始单号': str})

            # 获取表头，对表头进行转换成数据库字段名
            columns_key = df.columns.values.tolist()
            for i in range(len(columns_key)):
                if self.__class__.INIT_FIELDS_DIC.get(columns_key[i], None) is not None:
                    columns_key[i] = self.__class__.INIT_FIELDS_DIC.get(columns_key[i])

            # 验证一下必要的核心字段是否存在
            _ret_verify_field = TailOrder.verify_mandatory(columns_key)
            if _ret_verify_field is not None:
                report_dic['error'].append(_ret_verify_field)
                return report_dic

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
                _ret_verify_field = TailOrder.verify_mandatory(columns_key)
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
            _q_deliver_order = TailOrder.objects.filter(order_id=row['order_id'], mode_warehouse=1)
            if _q_deliver_order.exists():
                deliver_order = _q_deliver_order[0]
                deliver_order.track_no = row['track_no']

            else:
                report_dic["false"] += 1
                report_dic["error"].append("%s原始单号无法找到发货单" % row['order_id'])
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
        queryset = super(TOhandleAdmin, self).queryset()
        queryset = queryset.filter(order_status=1, is_delete=0, mode_warehouse=1)
        for obj in queryset:
            try:
                amount = obj.togoods_set.all().aggregate(
                    sum_product=Sum(F("quantity") * F('settlement_price'), output_field=models.FloatField()))["sum_product"]
                quantity = obj.togoods_set.all().aggregate(quantity=Sum('quantity'))['quantity']
            except Exception as e:
                amount = 0
            if amount is None:
                amount = 0
            obj.amount = amount
            obj.quantity = quantity
            obj.save()
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


class TOSpecialhandleAdmin(object):
    list_display = ['shop', 'order_id', 'ori_tail_order', 'quantity', 'order_category', 'mode_warehouse',
                    'track_no', 'sent_consignee', 'sent_smartphone', 'sent_city', 'sent_district', 'sent_address',
                    'submit_time', 'handle_time', 'handle_interval', 'message', 'sign_company', 'sign_department',
                    'process_tag', 'mistake_tag', 'order_status']

    actions = [CheckTOAction, RejectSelectedAction, ]
    list_exclude = ['amount', 'ori_amount', ]

    search_fields = ['order_id']
    list_filter = ['order_id', 'mode_warehouse', 'process_tag', 'creator', 'mistake_tag', 'order_category', 'sent_smartphone',
                   'submit_time', 'create_time']

    list_editable = ['track_no']
    readonly_fields = ['shop', 'sign_company', 'order_id', 'sent_city', 'sent_district', 'sent_address', 'message',
                       'sent_consignee', 'order_category', 'sent_smartphone', 'mode_warehouse',
                       'ori_tail_order', 'sent_province', 'quantity', 'ori_amount', 'amount', 'feedback']

    inlines = [TOGoodsInline]
    ALLOWED_EXTENSIONS = ['xls', 'xlsx']
    INIT_FIELDS_DIC = {"尾货订单": "order_id", "快递信息": "track_no"}
    import_data = True

    form_layout = [
        Fieldset('驳回信息',
                 'feedback', ),
        Fieldset('基本信息',
                 Row('shop', 'sign_company'),
                 Row('order_id', 'ori_tail_order',),
                 Row('order_category', 'message',),
                 Row('mode_warehouse', 'quantity',),),
        Fieldset('单号反馈信息',
                 'track_no', ),
        Fieldset('发货相关信息',
                 Row('sent_consignee', 'sent_smartphone'),
                 Row('sent_province', 'sent_city', 'sent_district'),
                 'sent_address'),
        Fieldset(None,
                 'submit_time', 'handle_time', 'handle_interval', 'process_tag', 'feedback', 'amount', 'ori_amount',
                 'mistake_tag', 'order_status', 'is_delete', 'creator', 'sign_company', 'sign_department',
                 **{"style": "display:None"}),
    ]

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file', None)
        if file:
            result = self.handle_upload_file(request, file)
            self.message_user('导入成功数据%s条' % int(result['successful']), 'success')
            if result['false'] > 0 or result['error']:
                self.message_user('导入失败数据%s条,主要的错误是%s' % (int(result['false']), result['error']), 'warning')
            if result['repeated'] > 0:
                self.message_user('包含更新重复数据%s条' % int(result['repeated']), 'error')
        return super(TOSpecialhandleAdmin, self).post(request, *args, **kwargs)

    def handle_upload_file(self, request, _file):
        report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error": []}
        if '.' in _file.name and _file.name.rsplit('.')[-1] in self.__class__.ALLOWED_EXTENSIONS:
            df = pd.read_excel(_file, sheet_name=0, converters={u'原始单号': str})

            # 获取表头，对表头进行转换成数据库字段名
            columns_key = df.columns.values.tolist()
            for i in range(len(columns_key)):
                if self.__class__.INIT_FIELDS_DIC.get(columns_key[i], None) is not None:
                    columns_key[i] = self.__class__.INIT_FIELDS_DIC.get(columns_key[i])

            # 验证一下必要的核心字段是否存在
            _ret_verify_field = TailOrder.verify_mandatory(columns_key)
            if _ret_verify_field is not None:
                report_dic['error'].append(_ret_verify_field)
                return report_dic

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
                _ret_verify_field = TailOrder.verify_mandatory(columns_key)
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
            _q_deliver_order = TailOrder.objects.filter(order_id=row['order_id'], mode_warehouse=0)
            if _q_deliver_order.exists():
                deliver_order = _q_deliver_order[0]
                deliver_order.track_no = row['track_no']

            else:
                report_dic["false"] += 1
                report_dic["error"].append("%s原始单号无法找到发货单" % row['order_id'])
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
        queryset = super(TOSpecialhandleAdmin, self).queryset()
        queryset = queryset.filter(order_status=1, is_delete=0, mode_warehouse=0)
        for obj in queryset:
            try:
                amount = obj.togoods_set.all().aggregate(
                    sum_product=Sum(F("quantity") * F('settlement_price'), output_field=models.FloatField()))["sum_product"]
                quantity = obj.togoods_set.all().aggregate(quantity=Sum('quantity'))['quantity']
            except Exception as e:
                amount = 0
            if amount is None:
                amount = 0
            obj.amount = amount
            obj.quantity = quantity
            obj.save()
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


class TailOrderAdmin(object):
    list_display = ['shop', 'order_id', 'ori_tail_order', 'track_no', 'amount', 'order_category', 'mode_warehouse',
                    'feedback', 'sent_consignee', 'sent_smartphone', 'sent_city', 'sent_district',
                    'sent_address', 'submit_time', 'handle_time', 'handle_interval', 'message',
                    'sign_company', 'sign_department', 'process_tag', 'mistake_tag', 'order_status']

    search_fields = ['sent_smartphone', 'track_no', 'order_id']
    list_filter = ['order_id', 'mode_warehouse', 'process_tag', 'creator', 'mistake_tag', 'order_category', 'sent_smartphone',
                   'submit_time', 'create_time']

    readonly_fields = ['shop', 'sign_company', 'order_id', 'sent_city', 'sent_district', 'sent_address', 'message',
                       'sent_consignee', 'order_category', 'sent_smartphone', 'mode_warehouse', 'track_no',
                       'ori_tail_order', 'sent_province', 'creator', 'submit_time', 'handle_time', 'quantity', 'amount',
                       'ori_amount', 'handle_interval', 'feedback', 'sign_department', 'process_tag', 'mistake_tag',
                       'order_status', 'is_delete',]

    inlines = [TOGoodsInline]
    relfield_style = 'fk-ajax'

    form_layout = [
        Fieldset('基本信息',
                 Row('shop', 'sign_company'),
                 Row('order_id', 'ori_tail_order',),
                 Row('order_category', 'message',),
                 Row('mode_warehouse', 'quantity',),),
        Fieldset('单号反馈信息',
                 'track_no', ),
        Fieldset('发货相关信息',
                 Row('sent_consignee', 'sent_smartphone'),
                 Row('sent_province', 'sent_city', 'sent_district'),
                 'sent_address'),
        Fieldset(None,
                 'submit_time', 'handle_time', 'handle_interval', 'process_tag', 'feedback', 'amount', 'ori_amount',
                 'mistake_tag', 'order_status', 'is_delete', 'creator', 'sign_company', 'sign_department',
                 **{"style": "display:None"}),
    ]

    def queryset(self):
        queryset = super(TailOrderAdmin, self).queryset()
        queryset = queryset.filter(is_delete=0)
        return queryset


# 重损仓未发货货品明细
class TOHGoodsAdmin(object):
    list_display = ['shop', 'tail_order', 'sent_consignee', 'sent_consignee', 'sent_address', 'sent_smartphone',
                    'sent_phone', 'deliver_condition', 'discounts', 'post_fee', 'receivable', 'settlement_price',
                    'settlement_amount', 'goods_id', 'goods_name', 'quantity', 'order_category', 'message',
                    'sent_province', 'sent_city', 'sent_district', 'track_no', 'mode_warehouse']

    readonly_fields = ['tail_order', 'goods_id', 'goods_name', 'quantity', 'price', 'memorandum', 'settlement_price',
                       'settlement_amount', 'goods_nickname', 'creator', 'amount']
    list_exclude = ['price', 'amount']
    list_filter = ['tail_order__sent_smartphone', 'goods_id', 'tail_order__mode_warehouse',
                   'goods_name', 'quantity', 'price', 'create_time', 'creator']
    search_fields = ['tail_order__sent_smartphone']

    form_layout = [
        Fieldset('基本信息',
                 Row('tail_order'),
                 ),
        Fieldset('货品信息',
                 Row('goods_id', 'goods_name', 'quantity', ),
                 ),
        Fieldset(None,
                 'settlement_price', 'settlement_amount', 'price', 'amount', 'creator', 'is_delete',
                 **{"style": "display:None"}),
    ]



    def has_add_permission(self):
        # 禁用添加按钮
        return False

    def queryset(self):
        queryset = super(TOHGoodsAdmin, self).queryset()
        queryset = queryset.filter(is_delete=0, tail_order__order_status=1, tail_order__mode_warehouse=1)
        return queryset


# 非重损仓未发货货品明细
class TOSGoodsAdmin(object):
    list_display = ['tail_order', 'sent_consignee', 'sent_smartphone', 'sent_province', 'sent_city', 'sent_district',
                    'sent_address', 'shop', 'goods_name',  'quantity', 'mode_warehouse', 'track_no', 'goods_id']

    readonly_fields = ['tail_order', 'goods_id', 'goods_name', 'quantity', 'price', 'memorandum', 'settlement_price',
                       'settlement_amount', 'goods_nickname', 'creator', 'amount']
    list_exclude = ['settlement_price', 'settlement_amount', 'price', 'amount']
    list_filter = ['tail_order__sent_smartphone', 'goods_id', 'tail_order__mode_warehouse',  'tail_order__track_no',
                   'goods_name', 'quantity', 'price', 'create_time', 'creator']
    search_fields = ['tail_order__sent_smartphone']

    form_layout = [
        Fieldset('基本信息',
                 Row('tail_order'),
                 ),
        Fieldset('货品信息',
                 Row('goods_id', 'goods_name', 'quantity', ),
                 ),
        Fieldset(None,
                 'settlement_price', 'settlement_amount', 'price', 'amount', 'creator', 'is_delete',
                 **{"style": "display:None"}),
    ]

    def has_add_permission(self):
        # 禁用添加按钮
        return False

    def queryset(self):
        queryset = super(TOSGoodsAdmin, self).queryset()
        queryset = queryset.filter(is_delete=0, tail_order__order_status=1, tail_order__mode_warehouse=0)
        return queryset


# 尾货订单发货明细
class TOGoodsAdmin(object):
    list_display = ['tail_order', 'mode_warehouse', 'shop', 'goods_name', 'goods_id', 'quantity', 'track_no',
                    'sent_consignee', 'sent_smartphone', 'sent_province', 'sent_city',
                    'sent_district', 'sent_address', ]

    readonly_fields = ['tail_order', 'goods_id', 'goods_name', 'quantity', 'price', 'memorandum', 'settlement_price',
                       'settlement_amount', 'goods_nickname', 'creator', 'amount']
    list_exclude = ['settlement_price', 'settlement_amount', 'price', 'amount']
    list_filter = ['tail_order__order_id', 'tail_order__sent_smartphone', 'goods_id', 'tail_order__mode_warehouse', 'tail_order__track_no',
                   'goods_name', 'quantity', 'price', 'create_time', 'creator']
    search_fields = ['tail_order__sent_smartphone']

    form_layout = [
        Fieldset('基本信息',
                 Row('tail_order'),
                 ),
        Fieldset('货品信息',
                 Row('goods_id', 'goods_name', 'quantity', ),
                 ),
        Fieldset(None,
                 'settlement_price', 'settlement_amount', 'price', 'amount', 'creator', 'is_delete',
                 **{"style": "display:None"}),
    ]

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 特殊权限尾货订单发货明细
class TOPrivilegeGoodsAdmin(object):
    list_display = ['tail_order', 'mode_warehouse', 'shop', 'goods_name', 'goods_id', 'quantity', 'price', 'amount',
                    'settlement_price', 'settlement_amount', 'track_no', 'message',  'order_status', 'refund_status',
                    'sent_consignee', 'sent_smartphone', 'sent_province', 'sent_city', 'sent_district',
                     'sent_address', 'submit_time',  'handle_time', 'handle_interval', ]

    readonly_fields = ['tail_order', 'goods_id', 'goods_name', 'quantity', 'price', 'memorandum', 'settlement_price',
                       'settlement_amount', 'goods_nickname', 'creator', 'amount']
    list_filter = ['tail_order__order_id', 'tail_order__sent_smartphone', 'goods_id', 'tail_order__mode_warehouse',
                   'tail_order__track_no', 'goods_name', 'quantity', 'price', 'create_time', 'creator',]
    search_fields = ['tail_order__order_id', 'tail_order__sent_smartphone', 'goods_nickname']

    form_layout = [
        Fieldset('基本信息',
                 Row('tail_order'),
                 ),
        Fieldset('货品信息',
                 Row('goods_id', 'goods_name', 'quantity', ),
                 Row('price', 'amount',),
                 Row('settlement_price', 'settlement_amount',),
                 ),
        Fieldset(None,
                 'creator', 'is_delete',
                 **{"style": "display:None"}),
    ]

    def has_add_permission(self):
        # 禁用添加按钮
        return False


class PBOGoodsInline(object):
    model = PBOGoods
    exclude = ['creator', 'goods_id', 'is_delete', 'goods_nickname', 'pb_order']

    extra = 1
    style = 'table'


# 付款结算单确认界面
class PBOSubmitAdmin(object):
    list_display = ['tail_order', 'order_id', 'track_no', 'process_tag', 'mistake_tag', 'order_category', 'sent_consignee',
                    'sent_smartphone', 'mode_warehouse', 'quantity', 'amount', 'creator', 'create_time', 'message',]
    actions = [SubmitPBOAction, RejectSelectedAction, ]

    search_fields = ['order_id']
    list_filter = ['mode_warehouse', 'process_tag', 'creator', 'mistake_tag', 'sent_smartphone',
                   'sent_consignee', 'order_category', 'create_time', 'tail_order__track_no']

    list_editable = ['message']
    readonly_fields = ['shop', 'sign_company', 'order_id', 'order_category', 'mode_warehouse', 'feedback', 'tail_order',
                       'quantity', 'amount', 'sign_department', 'sent_consignee', 'sent_smartphone']

    inlines = [PBOGoodsInline]

    form_layout = [
        Fieldset('驳回信息',
                 'message',
                 'feedback', ),
        Fieldset('基本信息',
                 Row('shop', 'sign_company'),
                 'order_id',
                 'order_category',
                 Row('mode_warehouse', 'quantity', 'amount',), ),
        Fieldset('发货相关信息',
                 Row('sent_consignee', 'sent_smartphone'),),
        Fieldset(None,
                 'submit_time', 'handle_time', 'handle_interval', 'process_tag', 'feedback',
                 'mistake_tag', 'order_status', 'is_delete', 'creator', 'sign_company', 'sign_department',
                 **{"style": "display:None"}),
    ]

    def queryset(self):
        queryset = super(PBOSubmitAdmin, self).queryset()
        queryset = queryset.filter(order_status=1, is_delete=0)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 付款结算单审核界面
class PBOCheckAdmin(object):
    list_display = ['tail_order', 'order_id', 'track_no', 'process_tag', 'mistake_tag', 'order_category', 'sent_consignee',
                    'sent_smartphone', 'mode_warehouse', 'quantity', 'amount', 'creator', 'create_time', 'message',]
    actions = [SetPBOAction, SetPBOCAction, CheckPBOAction]

    search_fields = ['order_id']
    list_filter = ['mode_warehouse', 'process_tag', 'creator', 'mistake_tag', 'sent_smartphone',
                   'sent_consignee', 'order_category', 'create_time', 'tail_order__track_no']

    list_editable = ['message']
    readonly_fields = ['shop', 'sign_company', 'order_id', 'order_category', 'mode_warehouse', 'feedback', 'tail_order',
                       'quantity', 'amount', 'sign_department', 'sent_consignee', 'sent_smartphone']

    inlines = [PBOGoodsInline]

    form_layout = [
        Fieldset('驳回信息',
                 'message',
                 'feedback', ),
        Fieldset('基本信息',
                 Row('shop', 'sign_company'),
                 'order_id',
                 'order_category',
                 Row('mode_warehouse', 'quantity', 'amount',), ),
        Fieldset('发货相关信息',
                 Row('sent_consignee', 'sent_smartphone'),),
        Fieldset(None,
                 'submit_time', 'handle_time', 'handle_interval', 'process_tag', 'feedback',
                 'mistake_tag', 'order_status', 'is_delete', 'creator', 'sign_company', 'sign_department',
                 **{"style": "display:None"}),
    ]
    batch_data = True
    delivery_ids = []

    def post(self, request, *args, **kwargs):
        delivery_ids = request.POST.get('ids', None)
        if delivery_ids is not None:
            if " " in delivery_ids:
                delivery_ids = delivery_ids.split(" ")
                for i in delivery_ids:
                    if not re.match(r'^[0-9a-zA-Z]+$', i):
                        self.message_user('%s包含错误的订单编号，请检查' % str(delivery_ids), 'error')
                        break

                self.delivery_ids = delivery_ids
                self.queryset()

        return super(PBOCheckAdmin, self).post(request, *args, **kwargs)

    def queryset(self):
        queryset = super(PBOCheckAdmin, self).queryset()
        if self.delivery_ids:
            queryset = queryset.filter(order_status=2, is_delete=0, tail_order__track_no__in=self.delivery_ids)
        else:
            queryset = queryset.filter(order_status=2, is_delete=0)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 付款结算单货品明细
class PBOGoodsAdmin(object):

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 付款结算单订单查询界面
class PayBillOrderAdmin(object):
    list_display = ['tail_order', 'order_status', 'order_id', 'track_no', 'process_tag', 'mistake_tag',
                    'order_category', 'sent_consignee', 'sent_smartphone', 'mode_warehouse', 'quantity',
                    'amount', 'creator', 'create_time', 'message',]

    search_fields = ['order_id']
    list_filter = ['mode_warehouse', 'process_tag', 'creator', 'mistake_tag', 'sent_smartphone', 'order_status',
                   'sent_consignee', 'order_category', 'create_time', 'tail_order__track_no']

    readonly_fields = ['shop', 'sign_company', 'order_id', 'order_category', 'mode_warehouse', 'feedback', 'tail_order',
                       'quantity', 'amount', 'sign_department', 'sent_consignee', 'sent_smartphone', 'message',
                       'creator', 'submit_time', 'handle_time', 'handle_interval', 'order_status', 'process_tag',
                       'mistake_tag']
    inlines = [PBOGoodsInline]

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 重损仓对账明细单审核界面
class AccountCheckAdmin(object):
    list_display = ['order_id', 'shop', 'mode_warehouse', 'order_category', 'goods_id', 'goods_name', 'goods_nickname',
                    'quantity', 'settlement_price', 'settlement_amount', 'sent_consignee', 'sent_smartphone',
                    'submit_time', 'handle_time', 'handle_interval', 'final_statement', 'message', 'feedback',
                    'order_status', 'process_tag', 'mistake_tag']
    list_filter = ['order_category', 'process_tag', 'mistake_tag', 'goods_id', 'quantity', 'settlement_price',
                   'settlement_amount', 'sent_consignee', 'sent_smartphone', 'submit_time', 'handle_time',]
    readonly_fields = ['order_id', 'shop', 'mode_warehouse', 'order_category', 'goods_id', 'goods_name',
                       'goods_nickname', 'quantity', 'settlement_price', 'settlement_amount', 'sent_consignee',
                       'sent_smartphone', 'submit_time', 'handle_time', 'handle_interval', 'final_statement',
                       'message', 'feedback', 'order_status', 'process_tag', 'mistake_tag', 'creator']
    actions = [CheckACCAction]

    def queryset(self):
        queryset = super(AccountCheckAdmin, self).queryset()
        queryset = queryset.filter(order_status=1, mode_warehouse=1, is_delete=0)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 非重损仓对账明细单审核界面
class AccountSpecialCheckAdmin(object):
    list_display = ['order_id', 'shop', 'mode_warehouse', 'order_category', 'goods_id', 'goods_name', 'goods_nickname',
                    'quantity', 'settlement_price', 'settlement_amount', 'sent_consignee', 'sent_smartphone',
                    'submit_time', 'handle_time', 'handle_interval', 'final_statement', 'message', 'feedback',
                    'order_status', 'process_tag', 'mistake_tag']
    list_filter = ['order_category', 'process_tag', 'mistake_tag', 'goods_id', 'quantity', 'settlement_price',
                   'settlement_amount', 'sent_consignee', 'sent_smartphone', 'submit_time', 'handle_time',]
    readonly_fields = ['order_id', 'shop', 'mode_warehouse', 'order_category', 'goods_id', 'goods_name',
                       'goods_nickname', 'quantity', 'settlement_price', 'settlement_amount', 'sent_consignee',
                       'sent_smartphone', 'submit_time', 'handle_time', 'handle_interval', 'final_statement',
                       'message', 'feedback', 'order_status', 'process_tag', 'mistake_tag', 'creator']
    actions = [CheckACCAction]

    def queryset(self):
        queryset = super(AccountSpecialCheckAdmin, self).queryset()
        queryset = queryset.filter(order_status=1, mode_warehouse=0, is_delete=0)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 未结算完成对账明细界面
class AccountUnfinishedAdmin(object):
    list_display = ['order_id', 'shop', 'mode_warehouse', 'order_category', 'goods_id', 'goods_name',
                    'goods_nickname', 'quantity', 'settlement_price', 'settlement_amount', 'sent_consignee', 'sent_smartphone',
                    'submit_time', 'handle_time', 'handle_interval', 'final_statement', 'message', 'feedback',
                    'order_status', 'process_tag', 'mistake_tag']
    readonly_fields = ['order_id', 'shop', 'mode_warehouse', 'order_category', 'goods_id', 'goods_name',
                       'goods_nickname', 'quantity', 'settlement_price', 'settlement_amount', 'sent_consignee',
                       'sent_smartphone', 'submit_time', 'handle_time', 'handle_interval', 'final_statement',
                       'message', 'feedback', 'order_status', 'process_tag', 'mistake_tag', 'creator',
                       'sign_department', 'sign_company']
    list_filter = ['order_category', 'mode_warehouse', 'process_tag', 'mistake_tag', 'goods_id', 'quantity',
                   'settlement_price', 'settlement_amount', 'sent_consignee', 'sent_smartphone', 'submit_time',
                   'handle_time',]

    def queryset(self):
        queryset = super(AccountUnfinishedAdmin, self).queryset()
        queryset = queryset.filter(order_status=2, mode_warehouse=0, is_delete=0)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 对账明细单查询界面
class AccountInfoAdmin(object):
    list_display = ['order_id', 'shop', 'mode_warehouse', 'order_category', 'goods_id', 'goods_name',
                    'goods_nickname', 'quantity', 'settlement_price', 'settlement_amount', 'sent_consignee', 'sent_smartphone',
                    'submit_time', 'handle_time', 'handle_interval', 'final_statement', 'message', 'feedback',
                    'order_status', 'process_tag', 'mistake_tag']
    readonly_fields = ['order_id', 'shop', 'mode_warehouse', 'order_category', 'goods_id', 'goods_name',
                       'goods_nickname', 'quantity', 'settlement_price', 'settlement_amount', 'sent_consignee',
                       'sent_smartphone', 'submit_time', 'handle_time', 'handle_interval', 'final_statement',
                       'message', 'feedback', 'order_status', 'process_tag', 'mistake_tag', 'creator',
                       'sign_department', 'sign_company']
    list_filter = ['order_category', 'mode_warehouse', 'process_tag', 'mistake_tag', 'goods_id', 'quantity',
                   'settlement_price', 'settlement_amount', 'sent_consignee', 'sent_smartphone', 'submit_time',
                   'handle_time',]



    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 付款单和对账单关联界面
class PBillToAccountAdmin(object):
    list_display = ['pbo_order', 'account_order']

    def has_add_permission(self):
        # 禁用添加按钮
        return False


class FSOGoodsInline(object):
    model = FinalStatementGoods
    exclude = ['creator', 'goods_id', 'is_delete', 'goods_nickname', 'fs_order']

    extra = 1
    style = 'table'


# 重损仓待确认账单
class FSAffirmAdmin(object):
    list_display = ['order_id', 'pay_order_id', 'message', 'feedback', 'mistake_tag', 'process_tag',
                    'mode_warehouse', 'quantity', 'amount', 'payee', 'bank', 'account']
    readonly_fields = ['order_id', 'message', 'mistake_tag', 'process_tag', 'creator', 'submit_time',
                       'mode_warehouse', 'quantity', 'amount', 'payee', 'bank', 'account', 'handle_time',
                       'handle_interval', 'order_status', 'pay_order_id', 'shop', 'sign_company', 'sign_department']
    list_editable = ['feedback']
    search_fields = ['order_id', 'pay_order_id',]
    list_filter = ['mistake_tag', 'process_tag', 'submit_time', 'mode_warehouse', 'quantity', 'amount', 'payee',
                   'bank', 'account']
    inlines = [FSOGoodsInline]

    actions = [AffirmFSAction]

    def queryset(self):
        queryset = super(FSAffirmAdmin, self).queryset()
        queryset = queryset.filter(order_status=1, mode_warehouse=1, is_delete=0)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 非重损仓待确认账单
class FSSpecialAffirmAdmin(object):
    list_display = ['order_id', 'pay_order_id', 'message', 'feedback', 'mistake_tag', 'process_tag',
                    'mode_warehouse', 'quantity', 'amount', 'payee', 'bank', 'account']
    readonly_fields = ['order_id', 'message', 'mistake_tag', 'process_tag', 'creator', 'submit_time',
                       'mode_warehouse', 'quantity', 'amount', 'payee', 'bank', 'account', 'handle_time',
                       'handle_interval', 'order_status', 'pay_order_id', 'shop', 'sign_company', 'sign_department']
    list_editable = ['feedback']
    search_fields = ['order_id', 'pay_order_id', ]
    list_filter = ['mistake_tag', 'process_tag', 'submit_time', 'mode_warehouse', 'quantity', 'amount', 'payee',
                   'bank', 'account']
    inlines = [FSOGoodsInline]

    actions = [AffirmFSAction]

    def queryset(self):
        queryset = super(FSSpecialAffirmAdmin, self).queryset()
        queryset = queryset.filter(order_status=1, mode_warehouse=0, is_delete=0)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 账单付款界面
class FSSubmitAdmin(object):
    list_display = ['order_id', 'pay_order_id', 'message', 'feedback', 'mistake_tag', 'process_tag',
                    'mode_warehouse', 'quantity', 'amount', 'payee', 'bank', 'account']
    readonly_fields = ['order_id', 'feedback', 'mistake_tag', 'process_tag', 'creator', 'submit_time',
                       'mode_warehouse', 'quantity', 'amount', 'payee', 'bank', 'account', 'handle_time',
                       'handle_interval', 'order_status', 'shop', 'sign_company', 'sign_department']
    list_editable = ['pay_order_id', 'message']
    search_fields = ['order_id']
    list_filter = ['mistake_tag', 'process_tag', 'submit_time', 'mode_warehouse', 'quantity', 'amount', 'payee',
                   'bank', 'account']
    inlines = [FSOGoodsInline]
    actions = [SubmitFSAction,]

    def queryset(self):
        queryset = super(FSSubmitAdmin, self).queryset()
        queryset = queryset.filter(order_status=2, is_delete=0)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 重损仓账单结算确认界面
class FSCheckAdmin(object):
    list_display = ['order_id', 'pay_order_id', 'message', 'feedback', 'mistake_tag', 'process_tag',
                    'mode_warehouse', 'quantity', 'amount', 'payee', 'bank', 'account']
    readonly_fields = ['order_id', 'message', 'mistake_tag', 'process_tag', 'creator', 'submit_time',
                       'mode_warehouse', 'quantity', 'amount', 'payee', 'bank', 'account', 'handle_time',
                       'handle_interval', 'order_status', 'pay_order_id', 'shop', 'sign_company', 'sign_department']
    list_editable = ['feedback']
    search_fields = ['order_id', 'pay_order_id',]
    list_filter = ['mistake_tag', 'process_tag', 'submit_time', 'mode_warehouse', 'quantity', 'amount', 'payee',
                   'bank', 'account']
    inlines = [FSOGoodsInline]

    actions = [SetFSAction, CheckFSAction, RejectSelectedAction]

    def queryset(self):
        queryset = super(FSCheckAdmin, self).queryset()
        queryset = queryset.filter(order_status=3, mode_warehouse=1, is_delete=0)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 非重损账单确认界面
class FSSpecialCheckAdmin(object):
    list_display = ['order_id', 'pay_order_id', 'message', 'feedback', 'mistake_tag', 'process_tag',
                    'mode_warehouse', 'quantity', 'amount', 'payee', 'bank', 'account']
    readonly_fields = ['order_id', 'message', 'mistake_tag', 'process_tag', 'creator', 'submit_time',
                       'mode_warehouse', 'quantity', 'amount', 'payee', 'bank', 'account', 'handle_time',
                       'handle_interval', 'order_status', 'pay_order_id', 'shop', 'sign_company', 'sign_department']
    list_editable = ['feedback']
    search_fields = ['order_id', 'pay_order_id',]
    list_filter = ['mistake_tag', 'process_tag', 'submit_time', 'mode_warehouse', 'quantity', 'amount', 'payee',
                   'bank', 'account']
    inlines = [FSOGoodsInline]

    actions = [SetFSAction, CheckFSAction, RejectSelectedAction]

    def queryset(self):
        queryset = super(FSSpecialCheckAdmin, self).queryset()
        queryset = queryset.filter(order_status=3, mode_warehouse=0, is_delete=0)
        return queryset


    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 账单查询界面
class FinalStatementAdmin(object):
    list_display = ['order_id', 'pay_order_id', 'message', 'feedback', 'mistake_tag', 'process_tag',
                    'mode_warehouse', 'quantity', 'amount', 'payee', 'bank', 'account']
    readonly_fields = ['order_id', 'message', 'mistake_tag', 'process_tag', 'creator', 'submit_time',
                       'mode_warehouse', 'quantity', 'amount', 'payee', 'bank', 'account', 'handle_time',
                       'handle_interval', 'order_status', 'pay_order_id', 'feedback', 'shop', 'sign_company',
                       'sign_department']
    search_fields = ['order_id', 'pay_order_id',]
    list_filter = ['mistake_tag', 'process_tag', 'submit_time', 'mode_warehouse', 'quantity', 'amount', 'payee',
                   'bank', 'account']
    inlines = [FSOGoodsInline]

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 账单货品明细界面
class FinalStatementGoodsAdmin(object):
    list_display = ['fs_order', 'order_category', 'goods_id', 'goods_name', 'goods_nickname', 'quantity',
                    'settlement_price', 'settlement_amount', 'memorandum']
    search_fields = ['fs_order__order_id', 'fs_order__pay_order_id', ]
    list_filter = ['order_category', 'goods_id', 'quantity', 'settlement_price', 'settlement_amount', 'create_time']

    def has_add_permission(self):
        # 禁用添加按钮
        return False


class ROGInline(object):
    model = ROGoods
    exclude = ['creator', 'goods_id', 'is_delete', 'goods_nickname', 'refund_order', 'receipted_quantity',
               'order_status', 'process_tag', 'mistake_tag']

    extra = 1
    style = 'table'


# 退换货单创建界面
class ROHandleAdmin(object):
    list_display = ['tail_order', 'order_id', 'process_tag', 'mistake_tag',  'shop', 'message', 'feedback',
                    'goods_name', 'order_category', 'info_refund', 'track_no', 'sent_consignee', 'sent_smartphone',
                    'sent_city', 'sent_district', 'sent_address', 'quantity', 'amount', 'mode_warehouse',
                    'sign_company',  'sign_department']
    actions = [SubimtROAction, RejectSelectedAction]
    search_fields = ['order_id']
    list_filter = []

    list_editable = ['message', 'track_no', 'info_refund', 'order_category', 'sent_consignee', 'sent_smartphone',
                    'sent_city', 'sent_district', 'sent_address',]
    readonly_fields = ['feedback', 'shop', 'order_id', 'quantity', 'amount', 'ori_amount',
                       'receipted_quantity', 'receipted_amount', 'submit_time', 'handle_time',
                       'handle_interval', 'sign_company', 'sign_department',
                       'process_tag', 'mistake_tag', 'order_status']

    inlines = [ROGInline]

    form_layout = [
        Fieldset('驳回信息',
                 'message',
                 'feedback',
                 'info_refund',),
        Fieldset('基本信息',
                 'tail_order',
                 'order_category',
                 'track_no',),
        Fieldset(None,
                 'shop', 'order_id', 'quantity', 'amount', 'ori_amount', 'creator', 'fast_tag', 'is_delete',
                 'receipted_quantity', 'receipted_amount', 'submit_time', 'handle_time',
                 'handle_interval', 'sign_company', 'sign_department',
                 'process_tag', 'mistake_tag', 'order_status', **{"style": "display:None"}),
    ]

    def save_models(self):
        obj = self.new_obj
        request = self.request
        if obj.fast_tag:
            i = 1
            while True:
                order_id = 'RO' + str(obj.tail_order.order_id) + "-" + str(i)
                if RefundOrder.objects.filter(order_id=order_id).exists():
                    i += 1
                else:
                    break
            obj.order_id = order_id
            obj.creator = request.user.username
            if not obj.sign_company:
                obj.sign_company = request.user.company
            if not obj.sign_department:
                obj.sign_department = self.request.user.department
            obj.ori_amount = obj.tail_order.amount
            fields_list = ['sent_consignee', 'sent_smartphone', 'sent_city', 'sent_district', 'sent_address', 'shop',
                           'mode_warehouse']
            for attr in fields_list:
                value = getattr(obj.tail_order, attr, None)
                setattr(obj, attr, value)
            obj.save()
            _q_goods_groups = obj.tail_order.togoods_set.all()
            for goods in _q_goods_groups:
                re_goods_order = ROGoods()
                re_goods_order.refund_order = obj
                re_goods_order.creator = request.user.username
                g_fields_list = ['goods_id', 'goods_name', 'goods_nickname', 'quantity', 'settlement_price', 'settlement_amount']
                for g_attr in g_fields_list:
                    value = getattr(goods, g_attr, None)
                    setattr(re_goods_order, g_attr, value)
                re_goods_order.receipted_quantity = 0
                re_goods_order.receipted_amount = 0
                re_goods_order.save()
            obj.fast_tag = 0
            obj.save()
        super().save_models()

    def queryset(self):
        queryset = super(ROHandleAdmin, self).queryset()
        queryset = queryset.filter(order_status=1, is_delete=0)

        for obj in queryset:
            try:
                amount = obj.rogoods_set.all().aggregate(
                    sum_product=Sum(F("quantity") * F('settlement_price'), output_field=models.FloatField()))["sum_product"]
                quantity = obj.rogoods_set.all().aggregate(quantity=Sum('quantity'))['quantity']
            except Exception as e:
                quantity = 0
                amount = 0
            if amount is None:
                amount = 0
            obj.amount = amount
            obj.quantity = quantity
            obj.save()
        return queryset


# 退换货单审核及待入库界面
class ROCheckAdmin(object):
    list_display = ['tail_order', 'mode_warehouse', 'process_tag', 'mistake_tag', 'message', 'feedback',  'shop',
                    'order_id', 'goods_name', 'order_category', 'info_refund', 'track_no', 'sent_consignee',
                    'sent_smartphone', 'sent_city', 'sent_district', 'sent_address', 'quantity', 'amount',
                    'ori_amount', 'receipted_quantity', 'receipted_amount',  'sign_company',  'sign_department']

    list_filter = ['tail_order__order_id',  'process_tag', 'mistake_tag',  'shop', 'order_category', 'create_time',
                   'sent_consignee', 'sent_smartphone', 'receipted_quantity', 'sign_company',
                   'sign_department', 'submit_time']
    search_fields = ['track_no']
    actions = [SetROAction, CheckROAction, RejectSelectedAction]

    list_editable = ['feedback', 'track_no']
    readonly_fields = ['message', 'shop', 'order_id', 'quantity', 'amount', 'ori_amount', 'creator', 'tail_order',
                       'receipted_quantity', 'receipted_amount', 'submit_time', 'handle_time', 'sent_consignee',
                       'sent_smartphone', 'sent_city', 'sent_district', 'sent_address', 'handle_interval',
                       'sign_company', 'sign_department', 'process_tag', 'mistake_tag', 'order_status',
                       'info_refund', 'order_category', 'fast_tag', 'track_no', 'mode_warehouse',]
    inlines = [ROGInline]
    batch_data = True
    delivery_ids = []

    def post(self, request, *args, **kwargs):
        delivery_ids = request.POST.get('ids', None)
        if delivery_ids is not None:
            if " " in delivery_ids:
                delivery_ids = delivery_ids.split(" ")
                for i in delivery_ids:
                    if not re.match(r'^[0-9a-zA-Z]+$', i):
                        self.message_user('%s包含错误的订单编号，请检查' % str(delivery_ids), 'error')
                        break

                self.delivery_ids = delivery_ids
                self.queryset()

        return super(ROCheckAdmin, self).post(request, *args, **kwargs)

    def queryset(self):
        queryset = super(ROCheckAdmin, self).queryset()
        if self.delivery_ids:
            queryset = queryset.filter(order_status=2, is_delete=0, track_no__in=self.delivery_ids)
        else:
            queryset = queryset.filter(order_status=2, is_delete=0)
        for obj in queryset:
            try:
                amount = obj.rogoods_set.all().filter(order_status__in=[3, 4]).aggregate(
                    sum_product=Sum(F("receipted_quantity") * F('settlement_price'), output_field=models.FloatField()))[
                    "sum_product"]
                quantity = obj.rogoods_set.all().filter(order_status__in=[3, 4]).aggregate(quantity=Sum(
                    'receipted_quantity'))['quantity']
            except Exception as e:
                quantity = 0
                amount = 0
            if amount is None:
                amount = 0
            if quantity is None:
                quantity = 0
            obj.receipted_amount = amount
            obj.receipted_quantity = quantity
            if obj.receipted_quantity:
                if obj.receipted_quantity == obj.quantity:
                    obj.process_tag = 6
                else:
                    obj.process_tag = 5
            obj.save()
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 退货单查询界面
class RefundOrderAdmin(object):
    list_display = ['tail_order',  'process_tag', 'mistake_tag',  'shop', 'order_id', 'order_category', 'info_refund',
                    'track_no', 'goods_name', 'sent_consignee', 'sent_smartphone', 'sent_city', 'sent_district',
                    'sent_address', 'quantity', 'amount', 'ori_amount', 'receipted_quantity', 'receipted_amount',
                    'mode_warehouse', 'message', 'feedback', 'sign_company',  'sign_department',  'order_status']
    inlines = [ROGInline]
    readonly_fields = ['tail_order',  'process_tag', 'mistake_tag',  'shop', 'order_id', 'order_category', 'info_refund',
                       'track_no', 'sent_consignee', 'sent_smartphone', 'sent_city', 'sent_district',
                       'sent_address', 'quantity', 'amount', 'ori_amount', 'receipted_quantity',
                       'receipted_amount',  'message', 'feedback', 'sign_company',  'sign_department',  'order_status']
    list_filter = ['process_tag', 'mistake_tag',  'shop', 'order_id', 'order_category', 'info_refund',
                    'track_no', 'sent_consignee', 'sent_smartphone', 'sent_city', 'sent_district',
                    'sent_address', 'quantity', 'amount', 'ori_amount', 'receipted_quantity',
                    'receipted_amount',  'message', 'feedback', 'sign_company',  'sign_department',  'order_status']

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 退货单货品入库界面
class ROGCheckAdmin(object):
    list_display = ['shop', 'refund_order', 'mistake_tag', 'goods_name', 'quantity', 'receipted_quantity',
                    'info_refund', 'track_no', 'sent_consignee', 'sent_smartphone', 'sent_city', 'sent_district',
                    'sent_address', 'message', 'order_status']
    search_fields = ['tail_order__track_no', 'tail_order__order_id']
    list_filter = []
    actions = [SetROGHAction, SetROGCAction, StockROGAction]

    list_editable = ['receipted_quantity']
    readonly_fields = ['order_status', 'refund_order', 'goods_id', 'goods_name', 'goods_nickname', 'quantity',
                       'settlement_price', 'settlement_amount', 'mistake_tag']
    batch_data = True
    delivery_ids = []

    def post(self, request, *args, **kwargs):
        delivery_ids = request.POST.get('ids', None)
        if delivery_ids is not None:
            if " " in delivery_ids:
                delivery_ids = delivery_ids.split(" ")
                for i in delivery_ids:
                    if not re.match(r'^[0-9a-zA-Z]+$', i):
                        self.message_user('%s包含错误的订单编号，请检查' % str(delivery_ids), 'error')
                        break

                self.delivery_ids = delivery_ids
                self.queryset()

        return super(ROGCheckAdmin, self).post(request, *args, **kwargs)

    def queryset(self):
        queryset = super(ROGCheckAdmin, self).queryset()
        if self.delivery_ids:
            queryset = queryset.filter(order_status__in=[2, 3], is_delete=0, tail_order__track_no__in=self.delivery_ids)
        else:
            queryset = queryset.filter(order_status__in=[2, 3], is_delete=0)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 退货单货品查询界面
class ROGoodsAdmin(object):
    list_display = ['shop', 'refund_order', 'mistake_tag', 'goods_name', 'quantity', 'receipted_quantity',
                    'info_refund', 'track_no', 'sent_consignee', 'sent_smartphone', 'sent_city', 'sent_district',
                    'sent_address', 'message', 'order_status']
    search_fields = []
    list_filter = ['refund_order__track_no', 'refund_order__order_id', 'refund_order__sent_smartphone', 'create_time',
                   'goods_id', 'quantity', 'receipted_quantity']
    readonly_fields = ['order_status', 'refund_order', 'goods_id', 'goods_name', 'goods_nickname', 'quantity',
                       'settlement_price', 'settlement_amount', 'mistake_tag', 'receipted_quantity', 'creator',
                       'process_tag', 'memorandum']

    def has_add_permission(self):
        # 禁用添加按钮
        return False


class ABOGInline(object):
    model = ABOGoods
    exclude = ['creator', 'goods_id', 'is_delete', 'goods_nickname', 'ab_order']

    extra = 1
    style = 'table'


# 退款单审核界面
class ABOSubmitAdmin(object):
    list_display = ['refund_order', 'process_tag', 'mistake_tag', 'shop', 'order_id', 'order_category', 'track_no',
                    'sent_consignee', 'sent_smartphone', 'settlement_quantity',
                    'settlement_amount', 'message', 'feedback', 'sign_company', 'sign_department']
    inlines = [ABOGInline]
    actions = [SetPBOAction, SetPBOCAction, CheckAOAction]
    list_filter = ['process_tag', 'mistake_tag', 'shop', 'order_id', 'order_category', 'refund_order__track_no',
                   'sent_consignee', 'sent_smartphone', 'settlement_quantity',
                   'settlement_amount',]

    readonly_fields = ['refund_order', 'process_tag', 'mistake_tag', 'shop', 'order_id', 'order_category',
                       'track_no', 'sent_consignee', 'sent_smartphone', 'settlement_quantity', 'is_delete',
                       'settlement_amount', 'message', 'feedback', 'sign_company', 'sign_department',
                       'creator', 'mode_warehouse', 'submit_time', 'handle_time', 'handle_interval', 'order_status']

    def queryset(self):
        queryset = super(ABOSubmitAdmin, self).queryset()
        queryset = queryset.filter(order_status=1, is_delete=0)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


class ABOCheckAdmin(object):
    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 退款结算单查询界面
class ArrearsBillOrderAdmin(object):
    list_display = ['refund_order', 'order_status', 'process_tag', 'mistake_tag', 'shop', 'order_id', 'order_category',
                    'track_no', 'sent_consignee', 'sent_smartphone', 'settlement_quantity',
                    'settlement_amount', 'message', 'feedback', 'sign_company', 'sign_department']
    inlines = [ABOGInline]

    readonly_fields = ['refund_order', 'process_tag', 'mistake_tag', 'shop', 'order_id', 'order_category',
                       'track_no', 'sent_consignee', 'sent_smartphone', 'settlement_quantity', 'is_delete',
                       'settlement_amount', 'message', 'feedback', 'sign_company', 'sign_department',
                       'creator', 'mode_warehouse', 'submit_time', 'handle_time', 'handle_interval', 'order_status']

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 退款结算货品明细界面
class ABOGoodsAdmin(object):

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 退款结算单关联对账单界面
class ABillToAccountAdmin(object):

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 提交赠品信息到订单
class SubmitTPOAction(BaseActionView):
    action_name = "submit_tpo"
    description = "提交选中的配件订单"
    model_perm = 'change'
    icon = "fa fa-flag"

    modify_models_batch = False

    @filter_hook
    def do_action(self, queryset):
        n = queryset.count()
        if not self.has_change_permission():
            raise PermissionDenied
        if n:
            for obj in queryset:
                _q_repeat_order = TailPartsOrder.objects.filter(sent_smartphone=obj.sent_smartphone, order_status=2)
                if _q_repeat_order.exists():
                    if obj.process_tag != 6:
                        self.message_user("%s电话重复" % obj.order_id, "error")
                        n -= 1
                        obj.mistakes = 12
                        obj.save()
                        continue
                if '整机' in obj.parts_info:
                    self.message_user("%s货品名称包含整机不是配件" % obj.order_id, "error")
                    n -= 1
                    obj.mistakes = 1
                    obj.save()
                    continue
                goods_group = self.goods_split(obj.parts_info)

                for goods_info in goods_group:
                    # 对货品进行处理
                    gift_order = GiftOrderInfo()

                    goods_list = str(goods_info).split("*")
                    if len(goods_list) == 2:
                        gift_order.quantity = goods_list[1]
                        goods_info = GoodsInfo.objects.filter(goods_name=goods_list[0])
                        if goods_info.exists():
                            gift_order.goods_name = goods_info[0].goods_name
                            gift_order.goods_id = goods_info[0].goods_id
                        else:
                            self.message_user("%s货品名称错误，修正后再次重新提交，如果名称无误，请联系管理员" % obj.order_id, "error")
                            n -= 1
                            obj.mistakes = 2
                            obj.save()
                            continue
                    order_id = str(obj.order_id).replace("订单号", "").replace(" ", "").replace("：", "")
                    gift_order.order_id = order_id

                    gift_order.nickname = str(obj.sent_consignee).replace("客户ID", "").replace(" ", "").replace("：", "").replace("顾客ID", "")
                    if len(gift_order.nickname) == 0:
                        self.message_user("%s收货人错误" % obj.order_id, "error")
                        n -= 1
                        obj.mistakes = 3
                        obj.save()
                        continue

                    # 用户名和货品确认递交是否是唯一
                    _gift_checked = GiftOrderInfo.objects.filter(goods_id=gift_order.goods_id, mobile=obj.sent_smartphone)
                    if _gift_checked.exists():
                        delta_date = (obj.create_time - _gift_checked[0].create_time).days
                        if obj.process_tag != 6:
                            if int(delta_date) > 14:
                                self.message_user("%s14天内重复" % obj.order_id, "error")
                                n -= 1
                                obj.mistakes = 5
                                obj.save()
                                continue
                            else:
                                self.message_user("%s14天外重复" % obj.order_id, "error")
                                n -= 1
                                obj.mistakes = 4
                                obj.save()
                                continue

                    gift_order.address = obj.sent_address
                    gift_order.receiver = obj.sent_consignee
                    gift_order.creator = obj.creator
                    gift_order.shop = obj.shop.shop_name
                    if gift_order.shop != '小狗尾货':
                        self.message_user("%s店铺错误" % obj.order_id, "error")
                        n -= 1
                        obj.mistakes = 11
                        obj.save()
                        continue

                    gift_order.order_category = obj.order_category
                    gift_order.shop = obj.shop.shop_name
                    gift_order.buyer_remark = "小狗尾货 %s客服%s赠送客户%s赠品%sx%s" % \
                                              (str(obj.update_time)[:11], self.request.user.username,
                                               gift_order.nickname, gift_order.goods_name, gift_order.quantity)
                    gift_order.cs_memoranda = "%sx%s" % (gift_order.goods_name, gift_order.quantity)
                    gift_order.submit_user = self.request.user.username
                    gift_order.mobile = obj.sent_smartphone
                    if re.match(r'^1', gift_order.mobile):
                        if len(gift_order.mobile) != 11:
                            self.message_user("%s手机出错" % obj.order_id, "error")
                            n -= 1
                            obj.mistakes = 6
                            obj.save()
                            continue
                    if '集运' in str(gift_order.address):
                        self.message_user("%s地址是集运仓" % obj.order_id, "error")
                        n -= 1
                        obj.mistakes = 7
                        obj.save()
                        continue
                    if not ((gift_order.receiver and gift_order.address) and gift_order.mobile):
                        self.message_user("%s收货人电话地址不全" % obj.order_id, "error")
                        n -= 1
                        obj.mistakes = 8
                        obj.save()
                        continue
                    if obj.sent_city:

                        gift_order.city = obj.sent_city
                        gift_order.province = obj.sent_city.province
                        gift_order.district = obj.sent_district
                    else:
                        self.message_user("%s城市错误" % obj.order_id, "error")
                        n -= 1
                        obj.mistakes = 9
                        obj.save()
                        continue
                    try:
                        gift_order.save()
                    except Exception as e:
                        self.message_user("%s出错:%s" % (obj.order_id, e), "error")
                        n -= 1
                        obj.mistakes = 10
                        obj.save()
                        continue

                    self.log('change', '', obj)
                    obj.order_status = 2
                    obj.mistake_tag = 0
                    obj.save()

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')
        return None

    def goods_split(self, goods):

        if "+" in goods:
            goods_group = goods.split("+")
        else:
            goods_group = [goods]

        for i in range(len(goods_group)):
            goods_group[i] = str(goods_group[i]).replace("\xa0", " ")
        return goods_group


# 提交赠品信息到订单
class SetTPOSAction(BaseActionView):
    action_name = "set_tpo_special"
    description = "设置选中为特殊订单"
    model_perm = 'change'
    icon = "fa fa-flag"

    modify_models_batch = False

    @filter_hook
    def do_action(self, queryset):
        n = queryset.count()
        if not self.has_change_permission():
            raise PermissionDenied
        if n:
            queryset.update(process_tag=6)
            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')
        return None


class SetTPOCAction(BaseActionView):
    action_name = "set_tpo_clear"
    description = "清除选中订单标记"
    model_perm = 'change'
    icon = "fa fa-flag"

    modify_models_batch = False

    @filter_hook
    def do_action(self, queryset):
        n = queryset.count()
        if not self.has_change_permission():
            raise PermissionDenied
        if n:
            queryset.update(process_tag=0)
            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')
        return None


# 售后赠品配件创建界面
class SubmitTPOAdmin(object):
    list_display = ['shop', 'order_id', 'process_tag', 'mistake_tag', 'sent_consignee', 'sent_smartphone', 'sent_city',
                    'sent_district', 'sent_address', 'parts_info', 'message', 'sign_company', 'sign_department',
                    'order_category', 'creator', 'create_time', 'update_time', 'order_status']
    actions = [SubmitTPOAction, SetTPOSAction, SetTPOCAction, RejectSelectedAction]

    search_fields = ['order_id']
    list_filter = ['sent_consignee', 'process_tag', 'creator', 'mistake_tag', 'parts_info', 'create_time']

    list_editable = ['sent_consignee', 'sent_smartphone', 'sent_city', 'sent_district', 'parts_info',
                     'sent_address', 'message',]

    readonly_fields = []

    form_layout = [
        Fieldset('基本信息',
                 'shop',  'parts_info', 'order_category',),
        Fieldset('发货相关信息',
                 Row('sent_consignee', 'sent_smartphone'),
                 Row('sent_city', 'sent_district'),
                 'sent_address'),
        Fieldset(None,
                 'process_tag', 'mistake_tag', 'order_status', 'is_delete', 'creator', 'sign_company', 'order_id',
                 'sign_department',  **{"style": "display:None"}),
    ]

    def save_models(self):
        obj = self.new_obj
        request = self.request
        obj.creator = request.user.username
        if not obj.order_id:
            i = 1
            while True:
                effective_value = len(str(i)) + 1
                bits = effective_value + 1
                base_num = 10 ** bits

                sn = base_num + int(i)
                prefix = "P"
                serial_number = str(datetime.datetime.now())
                serial_number = serial_number.replace("-", "")[:8]
                order_id = prefix + str(serial_number) + str(sn)[-effective_value:]
                _q_tpo_order = TailPartsOrder.objects.filter(order_id=order_id)
                if _q_tpo_order.exists():
                    i += 1
                else:
                    obj.order_id = order_id
                    break
        if not obj.sign_company:
            if request.user.company:
                obj.sign_company = request.user.company
        if not obj.sign_department:
            obj.sign_department = request.user.department
        obj.save()
        super().save_models()

    def queryset(self):
        queryset = super(SubmitTPOAdmin, self).queryset()
        queryset = queryset.filter(order_status=1, is_delete=0)
        return queryset


# 尾货配件查询界面
class TailPartsOrderAdmin(object):
    list_display = ['shop', 'order_id', 'process_tag', 'mistake_tag', 'sent_consignee', 'sent_smartphone', 'sent_city',
                    'sent_district', 'sent_address', 'parts_info', 'message', 'sign_company', 'sign_department',
                    'order_category', 'creator', 'create_time', 'update_time', 'order_status']

    search_fields = ['order_id']
    list_filter = ['sent_consignee', 'process_tag', 'creator', 'mistake_tag', 'parts_info', 'sent_smartphone',
                   'create_time']
    readonly_fields = ['shop', 'order_id', 'process_tag', 'mistake_tag', 'sent_consignee', 'sent_smartphone',
                       'sent_city', 'sent_district', 'sent_address', 'parts_info', 'message', 'sign_company',
                       'sign_department', 'order_status', 'order_category', 'creator', 'is_delete']

    def has_add_permission(self):
        # 禁用添加按钮
        return False


xadmin.site.register(OTOUnhandle, OTOUnhandleAdmin)
xadmin.site.register(OTOCheck, OTOCheckAdmin)
xadmin.site.register(OriTailOrder, OriTailOrderAdmin)
xadmin.site.register(OTOGoods, OTOGoodsAdmin)
xadmin.site.register(TOhandle, TOhandleAdmin)
xadmin.site.register(TOSpecialhandle, TOSpecialhandleAdmin)
xadmin.site.register(TailOrder, TailOrderAdmin)

xadmin.site.register(TOHGoods, TOHGoodsAdmin)
xadmin.site.register(TOSGoods, TOSGoodsAdmin)
xadmin.site.register(TOGoods, TOGoodsAdmin)
xadmin.site.register(TOPrivilegeGoods, TOPrivilegeGoodsAdmin)

xadmin.site.register(PBOSubmit, PBOSubmitAdmin)
xadmin.site.register(PBOCheck, PBOCheckAdmin)
xadmin.site.register(PBOGoods, PBOGoodsAdmin)
xadmin.site.register(PayBillOrder, PayBillOrderAdmin)

xadmin.site.register(AccountCheck, AccountCheckAdmin)
xadmin.site.register(AccountSpecialCheck, AccountSpecialCheckAdmin)
xadmin.site.register(AccountUnfinished, AccountUnfinishedAdmin)
xadmin.site.register(AccountInfo, AccountInfoAdmin)

xadmin.site.register(PBillToAccount, PBillToAccountAdmin)

xadmin.site.register(FSAffirm, FSAffirmAdmin)
xadmin.site.register(FSSpecialAffirm, FSSpecialAffirmAdmin)
xadmin.site.register(FSSubmit, FSSubmitAdmin)
xadmin.site.register(FSCheck, FSCheckAdmin)
xadmin.site.register(FSSpecialCheck, FSSpecialCheckAdmin)
xadmin.site.register(FinalStatement, FinalStatementAdmin)
xadmin.site.register(FinalStatementGoods, FinalStatementGoodsAdmin)

xadmin.site.register(ROHandle, ROHandleAdmin)
xadmin.site.register(ROCheck, ROCheckAdmin)
xadmin.site.register(RefundOrder, RefundOrderAdmin)
xadmin.site.register(ROGCheck, ROGCheckAdmin)
xadmin.site.register(ROGoods, ROGoodsAdmin)

xadmin.site.register(ABOSubmit, ABOSubmitAdmin)
# xadmin.site.register(ABOCheck, ABOCheckAdmin)
xadmin.site.register(ArrearsBillOrder, ArrearsBillOrderAdmin)
xadmin.site.register(ABOGoods, ABOGoodsAdmin)

xadmin.site.register(ABillToAccount, ABillToAccountAdmin)

xadmin.site.register(SubmitTPO, SubmitTPOAdmin)
xadmin.site.register(TailPartsOrder, TailPartsOrderAdmin)

