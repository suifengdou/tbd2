# -*- coding: utf-8 -*-
# @Time    : 2020/10/10 17:37
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
from django.db.models import Sum, Avg, Min, Max, F, Count

from django.contrib.admin.utils import get_deleted_objects

from django.core.files.uploadedfile import InMemoryUploadedFile

import xadmin
from xadmin.plugins.actions import BaseActionView
from xadmin.views.base import filter_hook
from xadmin.util import model_ngettext
from xadmin.layout import Fieldset, Main, Row, Side

from .models import OriOrderInfo, SubmitOriOrder, CheckOrder, SubmitOrder, SimpleOrder, OrderInfo, OriOrderList
from .models import PartWHCheckOrder, PartWHOrder, MachineWHCheckOrder, MachineWHOrder, CenterTWHCheckOrder
from .models import CenterTWHOrder, TailShopOrder, LabelOptions, OriBMSOrderInfo, SubmitOBMSOrder
from apps.crm.customers.models import CustomerInfo, OrderList, CountIdList
from apps.base.shop.models import ShopInfo
from apps.crm.cslabel.models import LabelInfo, LabelOrder, LabelDetial
from apps.crm.services.models import ServicesInfo, ServicesDetail

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

                if isinstance(obj, OriOrderInfo):
                    obj.order_status -= 1
                    obj.process_tag = 5
                    if obj.order_status == 0:
                        self.message_user("%s 取消成功" % obj.trade_no, "success")
                    obj.save()

                if isinstance(obj, OrderInfo):
                    obj.order_status -= 1
                    obj.process_tag = 5
                    if obj.order_status == 0:
                        obj.ori_order
                        self.message_user("%s 取消成功" % obj.trade_no, "success")
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


# 设置原始订单为特殊订单
class SetODSAction(BaseActionView):
    action_name = "set_od_special"
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


# 清除选中订单标签
class SetODCAction(BaseActionView):
    action_name = "set_od_clear"
    description = "清除选中订单标签"
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


# 直接设置递交成功
class SetODComplishAction(BaseActionView):
    action_name = "set_od_complish"
    description = "直接设置递交成功"
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
                if obj.process_tag != 6:
                    self.message_user("%s不是特殊订单" % obj.trade_no, "error")
                    n -= 1
                    continue
                else:
                    obj.order_status = 2
                    obj.process_tag = 7
                    obj.save()

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')
        return None


# 递交原始订单
class SubmitOriODAction(BaseActionView):
    action_name = "submit_ori_od"
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
                    self.log('change', '%s递交了原始订单' % self.request.user.username, obj)
                    if '*' in obj.buyer_nick:
                        try:
                            bms_order = OriBMSOrderInfo.objects.get(src_tids__exact=obj.src_tids)
                            if bms_order.buyer_nick:
                                obj.buyer_nick = bms_order.buyer_nick
                            else:
                                obj.buyer_nick = str(obj.buyer_nick).replace("*", '')
                            obj.receiver_address = bms_order.receiver_address
                            obj.receiver_mobile = bms_order.receiver_mobile
                            obj.receiver_name = bms_order.receiver_name
                        except OriBMSOrderInfo.DoesNotExist:
                            pass
                    _q_order_list = OriOrderList.objects.filter(ori_order=obj)
                    if _q_order_list.exists():
                        self.message_user("%s已导入过此订单" % obj.trade_no, "error")
                        n -= 1
                        obj.mistake_tag = 1
                        obj.save()
                    order = OrderInfo()
                    _q_order_id = OrderInfo.objects.filter(order_status__in=[1, 2, 3], trade_no=obj.trade_no)
                    if _q_order_id.exists():
                        if obj.process_tag != 6:
                            self.message_user("%s待确认重复订单" % obj.trade_no, "error")
                            n -= 1
                            obj.mistake_tag = 2
                            obj.save()
                            continue
                        else:
                            order.trade_no = '%s-%s' % (obj.trade_no, obj.id)
                    if not order.trade_no:
                        order.trade_no = obj.trade_no
                    fields_list = ['buyer_nick', 'receiver_name', 'receiver_address', 'receiver_mobile',
                                   'deliver_time', 'pay_time', 'receiver_area', 'logistics_no', 'buyer_message',
                                   'cs_remark', 'src_tids', 'num', 'price', 'share_amount', 'goods_name',
                                   'spec_code',
                                   'order_category', 'shop_name', 'logistics_name', 'warehouse_name']

                    order.ori_order = obj
                    for field in fields_list:
                        setattr(order, field, getattr(obj, field, None))
                    order_list = OriOrderList()
                    order_list.ori_order = obj
                    try:
                        order.creator = self.request.user.username
                        order.save()
                        obj.order_status = 2
                        obj.mistake_tag = 0
                        obj.save()
                        order_list.save()
                    except Exception as e:
                        n -= 1
                        self.message_user("%s递交错误：%s" % (obj.trade_no, e), "error")
            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')
        return None


# 递交订单到客户档案
class SubmitODAction(BaseActionView):
    action_name = "submit_od"
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
                    self.log('change', '%s递交了订单到客户档案' % self.request.user.username, obj)

                    repeat_tag = 0
                    ori_trade_id = obj.ori_order.trade_no
                    _q_ori_trade = CountIdList.objects.filter(ori_order_trade_no=ori_trade_id)
                    if _q_ori_trade.exists():
                        repeat_tag = 1
                    _q_order_list = OrderList.objects.filter(order=obj)
                    if _q_order_list.exists():
                        self.message_user("%s已导入过此订单" % obj.trade_no, "error")
                        n -= 1
                        obj.mistake_tag = 1
                        obj.save()
                    _q_customer_id = CustomerInfo.objects.filter(mobile=obj.receiver_mobile)
                    if _q_customer_id.exists():
                        customer_order = _q_customer_id[0]
                    else:
                        customer_order = CustomerInfo()
                        if re.match("^1\d{10}$", obj.receiver_mobile):
                            customer_order.mobile = obj.receiver_mobile

                    _q_shop = ShopInfo.objects.filter(shop_name=obj.shop_name)
                    if _q_shop.exists():
                        shop = _q_shop[0]
                    else:
                        self.message_user("%sUT中无此店铺，先创建店铺" % obj.trade_no, "error")
                        n -= 1
                        obj.mistake_tag = 2
                        obj.save()
                        continue
                    if shop.platform.platform:
                        id_table = {
                            "公司部门": "others_id",
                            "直营": "others_id",
                            "百度": "others_id",
                            "电视购物": "others_id",
                            "楚楚街": "others_id",
                            "拼多多": "pdd_id",
                            "快乐购": "others_id",
                            "小红书": "others_id",
                            "快手": "others_id",
                            "微信": "wechat",
                            "当当": "others_id",
                            "国美": "others_id",
                            "抖音": "others_id",
                            "亚马逊": "others_id",
                            "供应链": "others_id",
                            "经销商": "others_id",
                            "一号店": "others_id",
                            "速卖通": "others_id",
                            "自建": "gfsc_id",
                            "唯品会": "others_id",
                            "苏宁": "others_id",
                            "京东自营": "jdzy_id",
                            "京东FBP": "jdfbp_id",
                            "天猫": "wangwang",
                            "淘宝": "wangwang"
                        }
                        nickname_id = id_table.get(shop.platform.platform, None)
                        if nickname_id:
                            setattr(customer_order, nickname_id, obj.buyer_nick)
                        else:
                            self.message_user("%sUT中店铺，先关联平台" % obj.trade_no, "error")
                            n -= 1
                            obj.mistake_tag = 3
                            obj.save()
                            continue
                    if obj.shop_name != "供应平台":
                        if obj.share_amount > 0:
                            if obj.order_category in ["网店销售", "线下零售"]:
                                customer_order.total_amount += float(obj.share_amount)
                                if not repeat_tag:
                                    customer_order.total_times += 1
                                    customer_order.last_time = obj.deliver_time

                            elif obj.order_category in ["售后换货", "订单补发"]:
                                if not repeat_tag:
                                    customer_order.free_service_times += 1

                            elif obj.order_category in ["保修换新", "保修完成"]:
                                if not repeat_tag:
                                    customer_order.maintenance_times += 1
                        else:
                            if obj.order_category in ["售后换货", "订单补发", "线下零售"]:
                                if not repeat_tag:
                                    customer_order.free_service_times += 1

                            elif obj.order_category in ["保修换新", "保修完成"]:
                                if not repeat_tag:
                                    customer_order.maintenance_times += 1

                        order_list = OrderList()
                        order_count = CountIdList()
                        order_count.ori_order_trade_no = ori_trade_id
                        order_list.order = obj
                        order_list.creator = self.request.user.username
                        try:
                            if customer_order.mobile:
                                customer_order.creator = self.request.user.username
                                customer_order.save()
                            obj.order_status = 2
                            obj.mistake_tag = 0
                            obj.save()
                            order_list.save()
                            if not repeat_tag:
                                order_count.save()
                        except Exception as e:
                            self.message_user("%s保存出错：%s" % (obj.trade_no, e), "error")
                            n -= 1
                            obj.mistake_tag = 4
                            obj.save()
                            continue
                    else:
                        obj.order_status = 2
                        obj.mistake_tag = 0
                        obj.save()
            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')
        return None


# 订单批量自动标记客户
class LabelODAction(BaseActionView):
    action_name = "submit_od"
    description = "按整机型号标记选中的单据"
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
                parts_queryset = queryset.exclude(goods_name__contains='整机')
                parts_queryset.update(order_status=3)
                maintenance_queryset = queryset.filter(warehouse_name='苏州小狗维修仓')
                maintenance_queryset.update(order_status=3)
                machine_queryset = queryset.filter(goods_name__contains='整机', order_status=2)
                machine_queryset = machine_queryset.values_list("goods_name")
                machine_queryset = set(machine_queryset)
                for machine in machine_queryset:
                    label_order = LabelOrder()
                    serial_number = str(datetime.datetime.now())
                    serial_number = serial_number.replace("-", "").replace(" ", "").replace(":", "").replace(".", "")
                    label_order.order_id = str(serial_number) + str(machine[0]).replace(" ", "").replace("整机", "").replace(":", "").replace("：", "")

                    _q_label_name = LabelInfo.objects.filter(name=machine[0])
                    if _q_label_name.exists():
                        label = _q_label_name[0]
                        label_order.label = label
                    else:
                        label = LabelInfo()
                        label.name = machine[0]
                        label.order_category = 3
                        label.memorandum = '自动创建型号：%s的客户集群标签' % machine[0]
                        try:
                            label.creator = self.request.user.username
                            label.save()
                            label_order.label = label
                        except Exception as e:
                            self.message_user("%s保存标签出错：%s" % (label.name, e), "error")
                            continue

                    receiver_mobile_orders = queryset.filter(goods_name=machine[0])
                    receiver_mobiles = receiver_mobile_orders.values_list('receiver_mobile')
                    receiver_mobiles = set(receiver_mobiles)
                    label_order.quantity = len(receiver_mobiles)
                    try:
                        label_order.creator = self.request.user.username
                        label_order.save()
                    except Exception as e:
                        self.message_user("标签单据%s保存出错：%s" % (label_order.order_id, e), "error")
                        continue
                    for mobile in receiver_mobiles:
                        label_detial = LabelDetial()
                        _q_customer_info = CustomerInfo.objects.filter(mobile=mobile[0])

                        if _q_customer_info.exists():
                            label_detial.customer = _q_customer_info[0]
                        else:
                            self.message_user("%sUT中无此客户，无法创建标签" % mobile[0], "error")
                            label_order.quantity -= 1
                            label_order.save()
                            continue
                        label_detial.label_order = label_order
                        try:
                            label_detial.creator = self.request.user.username
                            label_detial.save()
                        except Exception as e:
                            self.message_user("标签单据明细%s保存出错：%s" % (label_detial.id, e), "error")
                            continue
                    receiver_mobile_orders.update(order_status=3)
            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')
        return None


# 创建客户关系任务
class CreateSOAction(BaseActionView):
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
                service_order.name = str(serial_number) + '订单创建任务-需要改名'
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


# 创建旗舰店旺旺留言任务
class CreatePWSAction(BaseActionView):
    action_name = "create_part_wangwang"
    description = "创建配件旺旺留言关系任务"
    model_perm = 'change'
    icon = "fa fa-flag"

    modify_models_batch = False

    @filter_hook
    def do_action(self, queryset):
        queryset = queryset.filter(shop_name='小狗电器旗舰店')
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
                service_order.name = str(serial_number) + '配件发货单旺旺留言'
                service_order.prepare_time = datetime.datetime.now()
                service_order.order_type = 1
                service_order.order_category = 3
                service_order.quantity = n
                service_order.memorandum = '%s 在配件仓订单创建了客户关系任务' % self.request.user.username
                try:
                    service_order.creator = self.request.user.username
                    service_order.save()
                except Exception as e:
                    self.message_user("创建配件发货单旺旺留言任务订单保存出错：%s" % e, "error")
                    return None
                for obj in queryset:

                    self.log('change', '%s创建了客户关系任务' % self.request.user.username, obj)
                    _q_customer = CustomerInfo.objects.filter(mobile=obj.receiver_mobile)
                    if _q_customer.exists():
                        customer = _q_customer[0]
                    else:
                        self.message_user("%s无此客户，未创建对应任务" % obj.receiver_mobile, "error")
                        continue

                    service_detail = ServicesDetail()
                    service_detail.customer = customer
                    service_detail.services = service_order
                    service_detail.target = obj.buyer_nick
                    service_detail.memorandum = '%s的快递信息：%s单号：%s，还请您留意' % (str(obj.goods_name),
                                                                                    str(obj.logistics_name),
                                                                                    str(obj.logistics_no))
                    try:
                        service_detail.creator = self.request.user.username
                        service_detail.save()
                    except Exception as e:
                        self.message_user("创建配件发货单任务订单明细保存出错：%s" % e, "error")
                        continue

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')
        return None


# 创建旗舰店旺旺留言任务
class CreateGWSAction(BaseActionView):
    action_name = "create_gift_wangwang"
    description = "创建礼品旺旺留言关系任务"
    model_perm = 'change'
    icon = "fa fa-flag"

    modify_models_batch = False

    @filter_hook
    def do_action(self, queryset):
        queryset = queryset.filter(shop_name='小狗电器旗舰店')
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
                service_order.name = str(serial_number) + '礼品发货单旺旺留言'
                service_order.prepare_time = datetime.datetime.now()
                service_order.order_type = 1
                service_order.order_category = 3
                service_order.quantity = n
                service_order.memorandum = '%s 在整机仓订单创建了客户关系任务' % self.request.user.username
                try:
                    service_order.creator = self.request.user.username
                    service_order.save()
                except Exception as e:
                    self.message_user("创建礼品发货单旺旺留言任务订单保存出错：%s" % e, "error")
                    return None
                for obj in queryset:

                    self.log('change', '%s创建了客户关系任务' % self.request.user.username, obj)
                    _q_customer = CustomerInfo.objects.filter(mobile=obj.receiver_mobile)
                    if _q_customer.exists():
                        customer = _q_customer[0]
                    else:
                        self.message_user("%s无此客户，未创建对应任务" % obj.receiver_mobile, "error")
                        continue

                    service_detail = ServicesDetail()
                    service_detail.customer = customer
                    service_detail.services = service_order
                    service_detail.target = obj.buyer_nick
                    service_detail.memorandum = '%s的快递信息：%s单号：%s，还请您留意' % (str(obj.goods_name),
                                                                           str(obj.logistics_name),
                                                                           str(obj.logistics_no))
                    try:
                        service_detail.creator = self.request.user.username
                        service_detail.save()
                    except Exception as e:
                        self.message_user("创建礼品发货单任务订单明细保存出错：%s" % e, "error")
                        continue

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')
        return None


# 递交订单到客户档案
class CorrectionODAction(BaseActionView):
    action_name = "correction_od"
    description = "校正选中的单据"
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
                    self.log('change', '%s修正了原始订单' % self.request.user.username, obj)
                    _q_ori_order = OriOrderInfo.objects.filter(src_tids__exact=obj.src_tids)
                    if _q_ori_order.exists():
                        for ori_order in _q_ori_order:
                            if '*' in ori_order.receiver_name:
                                if obj.buyer_nick:
                                    ori_order.buyer_nick = obj.buyer_nick
                                else:
                                    ori_order.buyer_nick = str(ori_order.buyer_nick).replace("*", '')
                                ori_order.receiver_address = obj.receiver_address
                                ori_order.receiver_mobile = obj.receiver_mobile
                                ori_order.receiver_name = obj.receiver_name
                                ori_order.save()
                    _q_order = OrderInfo.objects.filter(src_tids__exact=obj.src_tids)
                    if _q_order.exists():
                        for order in _q_order:
                            if '*' in order.receiver_name:
                                if obj.buyer_nick:
                                    order.buyer_nick = obj.buyer_nick
                                else:
                                    order.buyer_nick = str(order.buyer_nick).replace("*", '')
                                order.receiver_mobile = obj.receiver_mobile
                                order.receiver_address = obj.receiver_address
                                order.receiver_name = obj.receiver_name
                                order.order_status = 1
                                order.save()
                    obj.order_status = 2
                    obj.mistake_tag = 0
                    obj.save()
            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')
        return None


# 提交原始订单界面
class SubmitOriOrderAdmin(object):
    list_display = ['trade_no', 'process_tag', 'mistake_tag', 'shop_name', 'warehouse_name', 'buyer_nick',
                    'receiver_name', 'receiver_area', 'receiver_address', 'receiver_mobile', 'goods_name', 'spec_code',
                    'num', 'price', 'share_amount', 'pay_time', 'deliver_time', 'logistics_name', 'logistics_no',
                    'buyer_message', 'cs_remark', 'order_status', 'src_tids']

    list_filter = ['trade_no', 'process_tag', 'mistake_tag', 'buyer_nick', 'receiver_mobile', 'deliver_time',
                   'goods_name', 'spec_code', 'num', 'price','share_amount', 'src_tids', 'creator']
    actions = [SetODSAction, SetODCAction, SetODComplishAction, SubmitOriODAction, RejectSelectedAction]

    form_layout = [
        Fieldset('基本信息',
                 Row('shop_name', 'warehouse_name', 'buyer_nick', ),

                 Row('receiver_name', 'receiver_address', 'receiver_mobile', ),
                 Row('goods_name', 'spec_code', 'num',
                     'price', 'share_amount', ),
                 Row('deliver_time', 'logistics_name', 'logistics_no', ), ),
        Fieldset(None,
                 'creator', 'create_time', 'update_time', 'is_delete', **{"style": "display:None"}),
    ]
    ALLOWED_EXTENSIONS = ['xls', 'xlsx']
    INIT_FIELDS_DIC = {
        '客户网名': 'buyer_nick',
        '订单编号': 'trade_no',
        '收件人': 'receiver_name',
        '收货地址': 'receiver_address',
        '收件人手机': 'receiver_mobile',
        '发货时间': 'deliver_time',
        '付款时间': 'pay_time',
        '收货地区': 'receiver_area',
        '物流单号': 'logistics_no',
        '买家留言': 'buyer_message',
        '客服备注': 'cs_remark',
        '原始单号': 'src_tids',
        '货品数量': 'num',
        '货品成交价': 'price',
        '货品成交总价': 'share_amount',
        '货品名称': 'goods_name',
        '商家编码': 'spec_code',
        '店铺': 'shop_name',
        '物流公司': 'logistics_name',
        '仓库': 'warehouse_name',
        '订单类型': 'order_category',

    }

    import_data = True

    def post(self, request, *args, **kwargs):

        file = request.FILES.get('file', None)
        if file:
            result = self.handle_upload_file(request, file)
            self.message_user('结果提示：%s' % result)
        return super(SubmitOriOrderAdmin, self).post(request, *args, **kwargs)

    def handle_upload_file(self, request, _file):
        report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error": []}
        if '.' in _file.name and _file.name.rsplit('.')[-1] in self.__class__.ALLOWED_EXTENSIONS:
            df = pd.read_excel(_file, sheet_name=0, dtype=str)

            FILTER_FIELDS = ['客户网名', '订单编号', '收件人', '收货地址', '收件人手机', '发货时间', '付款时间', '收货地区',
                             '物流单号', '买家留言', '客服备注', '原始单号', '货品数量', '货品成交价', '货品成交总价', '货品名称',
                             '商家编码', '店铺', '物流公司', '仓库', '订单类型']

            try:
                df = df[FILTER_FIELDS]
            except Exception as e:
                report_dic["error"].append(e)
                return report_dic

            # 获取表头，对表头进行转换成数据库字段名
            columns_key = df.columns.values.tolist()
            for i in range(len(columns_key)):
                if self.__class__.INIT_FIELDS_DIC.get(columns_key[i], None) is not None:
                    columns_key[i] = self.__class__.INIT_FIELDS_DIC.get(columns_key[i])

            # 验证一下必要的核心字段是否存在
            _ret_verify_field = OriOrderInfo.verify_mandatory(columns_key)
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

        else:
            report_dic["error"].append('只支持excel文件格式！')
            return report_dic

    @staticmethod
    def save_resources(request, resource):
        # 设置初始报告
        report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error":[]}

        for row in resource:
            if row['trade_no'] == '合计:':
                continue
            if "0000-00-00" in str(row['pay_time']):
                row['pay_time'] = row['deliver_time']
            emo_fields = ['buyer_nick', 'receiver_name', 'receiver_address', 'buyer_message', 'cs_remark']
            for word in emo_fields:
                row[word] = emoji.demojize(str(row[word]))

            order_fields = ['buyer_nick', 'trade_no', 'receiver_name', 'receiver_address', 'receiver_mobile',
                            'deliver_time', 'pay_time', 'receiver_area', 'logistics_no', 'buyer_message', 'cs_remark',
                            'src_tids', 'num', 'price', 'share_amount', 'goods_name', 'spec_code', 'order_category',
                            'shop_name', 'logistics_name', 'warehouse_name']
            order = OriOrderInfo()
            for field in order_fields:
                if row[field] in ['nan', 'NaN']:
                    row[field] = ''
                setattr(order, field, row[field])
            if not order.src_tids:
                order.src_tids = order.trade_no
            if len(order.scr_tids) > 100:
                order.src_tids = str(order.src_tids)[:100]
            try:
                order.creator = request.user.username
                order.save()
                report_dic["successful"] += 1
            except Exception as e:
                report_dic['error'].append(e)
                report_dic["false"] += 1

        return report_dic

    def queryset(self):
        queryset = super(SubmitOriOrderAdmin, self).queryset()
        queryset = queryset.filter(order_status=1)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 原始订单查询
class OriOrderInfoAdmin(object):
    list_display = ['trade_no', 'process_tag', 'mistake_tag', 'shop_name', 'warehouse_name', 'buyer_nick',
                    'receiver_name', 'receiver_area', 'receiver_address', 'receiver_mobile', 'goods_name', 'spec_code',
                    'num', 'price', 'share_amount', 'pay_time', 'deliver_time', 'logistics_name', 'logistics_no',
                    'buyer_message', 'cs_remark', 'order_status', 'src_tids']

    list_filter = ['trade_no', 'process_tag', 'mistake_tag', 'buyer_nick', 'receiver_mobile', 'deliver_time',
                   'goods_name', 'spec_code', 'num', 'price', 'share_amount', 'src_tids', 'creator']

    readonley_fields = ['trade_no', 'process_tag', 'mistake_tag', 'shop_name', 'warehouse_name', 'buyer_nick',
                        'receiver_name', 'receiver_area', 'receiver_address', 'receiver_mobile', 'goods_name',
                        'spec_code', 'num', 'price', 'share_amount', 'pay_time', 'deliver_time', 'logistics_name',
                        'logistics_no', 'buyer_message', 'cs_remark', 'order_status', 'src_tids', 'creator',
                        'is_delete', 'create_time', 'update_time']

    form_layout = [
        Fieldset('基本信息',
                 Row('shop_name', 'warehouse_name', 'buyer_nick',),

                 Row('receiver_name', 'receiver_address', 'receiver_mobile',),
                 Row('goods_name', 'spec_code', 'num',
                     'price', 'share_amount', ),
                 Row('deliver_time', 'logistics_name', 'logistics_no', ),),
        Fieldset(None,
                 'creator', 'create_time', 'update_time', 'is_delete', **{"style": "display:None"}),
    ]


    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 极简订单快速查询
class SimpleOrderAdmin(object):
    list_display = ['trade_no', 'buyer_nick', 'cs_info', 'src_tids', 'goods_name', 'spec_code', 'order_status',
                    'num', 'price', 'share_amount', 'pay_time', 'deliver_time', 'logistics_name', 'logistics_no',
                    'order_category', 'warehouse_name']
    readonley_fields = ['trade_no', 'process_tag', 'mistake_tag', 'shop_name', 'warehouse_name', 'buyer_nick',
                        'receiver_name', 'receiver_area', 'receiver_address', 'receiver_mobile', 'goods_name',
                        'spec_code', 'num', 'price', 'share_amount', 'pay_time', 'deliver_time', 'logistics_name',
                        'logistics_no', 'buyer_message', 'cs_remark', 'order_status', 'src_tids', 'creator',
                        'is_delete', 'create_time', 'update_time']

    form_layout = [
        Fieldset('基本信息',
                 Row('buyer_nick',),
                 Row('cs_info',), ),
        Fieldset(None,
                 'creator', 'create_time', 'update_time', 'is_delete', **{"style": "display:None"}),
    ]

    batch_data = True
    nick_ids = []

    def post(self, request, *args, **kwargs):
        ids = request.POST.get('ids', None)
        if ids is not None:
            if " " in ids:
                ids = ids.split(" ")
                self.nick_ids = []
                self.nick_ids = ids
                self.queryset()
            else:
                self.nick_ids = []
                self.nick_ids.append(str(ids).replace("/t", "").replace("/n", "").replace(" ", ""))
                self.queryset()

        return super(SimpleOrderAdmin, self).post(request, *args, **kwargs)

    def queryset(self):
        queryset = super(SimpleOrderAdmin, self).queryset()

        if self.nick_ids:
            queryset = queryset.filter(is_delete=0, buyer_nick__in=self.nick_ids)
            if not queryset:
                queryset = super(SimpleOrderAdmin, self).queryset().filter(is_delete=0, receiver_mobile__in=self.nick_ids)
        else:
            queryset = queryset.filter(id=0)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 递交订单
class SubmitOrderAdmin(object):
    list_display = ['trade_no', 'process_tag', 'mistake_tag', 'shop_name', 'warehouse_name', 'buyer_nick',
                    'receiver_name', 'receiver_area', 'receiver_address', 'receiver_mobile', 'goods_name', 'spec_code',
                    'num', 'price', 'share_amount', 'pay_time', 'deliver_time', 'logistics_name', 'logistics_no',
                    'buyer_message', 'cs_remark', 'order_status', 'src_tids']

    list_filter = ['process_tag', 'mistake_tag', 'trade_no', 'buyer_nick', 'receiver_mobile', 'deliver_time',
                   'goods_name', 'spec_code', 'num', 'price', 'share_amount', 'src_tids', 'creator']
    readonley_fields = ['trade_no', 'process_tag', 'mistake_tag', 'shop_name', 'warehouse_name', 'buyer_nick',
                        'receiver_name', 'receiver_area', 'receiver_address', 'receiver_mobile', 'goods_name',
                        'spec_code', 'num', 'price', 'share_amount', 'pay_time', 'deliver_time', 'logistics_name',
                        'logistics_no', 'buyer_message', 'cs_remark', 'order_status', 'src_tids', 'creator',
                        'is_delete', 'create_time', 'update_time']
    actions = [SetODCAction, SetODCAction, SubmitODAction, RejectSelectedAction]

    form_layout = [
        Fieldset('基本信息',
                 Row('shop_name', 'warehouse_name', 'buyer_nick', ),

                 Row('receiver_name', 'receiver_address', 'receiver_mobile', ),
                 Row('goods_name', 'spec_code', 'num',
                     'price', 'share_amount', ),
                 Row('deliver_time', 'logistics_name', 'logistics_no', ), ),
        Fieldset(None,
                 'creator', 'create_time', 'update_time', 'is_delete', **{"style": "display:None"}),
    ]

    def queryset(self):
        queryset = super(SubmitOrderAdmin, self).queryset()
        queryset = queryset.filter(is_delete=0, order_status=1)

        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 可标签查询
class LabelOptionsAdmin(object):
    list_display = ['trade_no', 'process_tag', 'mistake_tag', 'shop_name', 'warehouse_name', 'buyer_nick',
                    'receiver_name', 'receiver_area', 'receiver_address', 'receiver_mobile', 'goods_name',
                    'spec_code',
                    'num', 'price', 'share_amount', 'pay_time', 'deliver_time', 'logistics_name', 'logistics_no',
                    'buyer_message', 'cs_remark', 'order_status', 'src_tids']
    readonley_fields = ['trade_no', 'process_tag', 'mistake_tag', 'shop_name', 'warehouse_name', 'buyer_nick',
                        'receiver_name', 'receiver_area', 'receiver_address', 'receiver_mobile', 'goods_name',
                        'spec_code', 'num', 'price', 'share_amount', 'pay_time', 'deliver_time', 'logistics_name',
                        'logistics_no', 'buyer_message', 'cs_remark', 'order_status', 'src_tids', 'creator',
                        'is_delete', 'create_time', 'update_time']

    actions = [LabelODAction]

    list_filter = ['process_tag', 'mistake_tag', 'trade_no', 'buyer_nick', 'receiver_mobile', 'deliver_time',
                   'goods_name', 'spec_code', 'num', 'price', 'share_amount', 'src_tids', ]

    form_layout = [
        Fieldset('基本信息',
                 Row('shop_name', 'warehouse_name', 'buyer_nick', ),

                 Row('receiver_name', 'receiver_address', 'receiver_mobile', ),
                 Row('goods_name', 'spec_code', 'num',
                     'price', 'share_amount', ),
                 Row('deliver_time', 'logistics_name', 'logistics_no', ), ),
        Fieldset(None,
                 'creator', 'create_time', 'update_time', 'is_delete', **{"style": "display:None"}),
    ]

    def queryset(self):
        queryset = super(LabelOptionsAdmin, self).queryset().filter(order_status=2, is_delete=0)
        return queryset


# 审核订单
class CheckOrderAdmin(object):
    list_display = ['trade_no', 'process_tag', 'mistake_tag', 'shop_name', 'warehouse_name', 'buyer_nick',
                    'receiver_name', 'receiver_area', 'receiver_address', 'receiver_mobile', 'goods_name',
                    'spec_code',
                    'num', 'price', 'share_amount', 'pay_time', 'deliver_time', 'logistics_name', 'logistics_no',
                    'buyer_message', 'cs_remark', 'order_status', 'src_tids']
    readonley_fields = ['trade_no', 'process_tag', 'mistake_tag', 'shop_name', 'warehouse_name', 'buyer_nick',
                        'receiver_name', 'receiver_area', 'receiver_address', 'receiver_mobile', 'goods_name',
                        'spec_code', 'num', 'price', 'share_amount', 'pay_time', 'deliver_time', 'logistics_name',
                        'logistics_no', 'buyer_message', 'cs_remark', 'order_status', 'src_tids', 'creator',
                        'is_delete', 'create_time', 'update_time']

    list_filter = ['process_tag', 'mistake_tag', 'trade_no', 'buyer_nick', 'receiver_mobile', 'deliver_time',
                   'goods_name', 'spec_code', 'num', 'price', 'share_amount', 'src_tids', ]

    form_layout = [
        Fieldset('基本信息',
                 Row('shop_name', 'warehouse_name', 'buyer_nick', ),

                 Row('receiver_name', 'receiver_address', 'receiver_mobile', ),
                 Row('goods_name', 'spec_code', 'num',
                     'price', 'share_amount', ),
                 Row('deliver_time', 'logistics_name', 'logistics_no', ), ),
        Fieldset(None,
                 'creator', 'create_time', 'update_time', 'is_delete', **{"style": "display:None"}),
    ]

    def queryset(self):
        queryset = super(CheckOrderAdmin, self).queryset()
        queryset = queryset.filter(is_delete=0, order_status=3)

        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 订单查询
class OrderInfoAdmin(object):
    list_display = ['trade_no', 'process_tag', 'mistake_tag', 'shop_name', 'warehouse_name', 'buyer_nick',
                    'receiver_name', 'receiver_area', 'receiver_address', 'receiver_mobile', 'goods_name', 'spec_code',
                    'num', 'price', 'share_amount', 'pay_time', 'deliver_time', 'logistics_name', 'logistics_no',
                    'buyer_message', 'cs_remark', 'order_status', 'src_tids']
    readonley_fields = ['trade_no', 'process_tag', 'mistake_tag', 'shop_name', 'warehouse_name', 'buyer_nick',
                        'receiver_name', 'receiver_area', 'receiver_address', 'receiver_mobile', 'goods_name',
                        'spec_code', 'num', 'price', 'share_amount', 'pay_time', 'deliver_time', 'logistics_name',
                        'logistics_no', 'buyer_message', 'cs_remark', 'order_status', 'src_tids', 'creator',
                        'is_delete', 'create_time', 'update_time']
    actions = [CreateSOAction]

    list_filter = ['create_time', 'shop_name', 'goods_name', 'process_tag', 'mistake_tag', 'trade_no', 'buyer_nick',
                   'receiver_mobile', 'deliver_time', 'spec_code', 'num', 'price', 'share_amount', 'src_tids', ]

    form_layout = [
        Fieldset('基本信息',
                 Row('shop_name', 'warehouse_name', 'buyer_nick', ),

                 Row('receiver_name', 'receiver_address', 'receiver_mobile', ),
                 Row('goods_name', 'spec_code', 'num',
                     'price', 'share_amount', ),
                 Row('deliver_time', 'logistics_name', 'logistics_no', ), ),
        Fieldset(None,
                 'creator', 'create_time', 'update_time', 'is_delete', **{"style": "display:None"}),
    ]

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 原始订单导入列表
class OriOrderListAdmin(object):

    list_display = ['ori_order', 'creator', 'create_time']
    list_filter = ['ori_order__trade_no']

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 配件仓未关联订单
class PartWHCheckOrderAdmin(object):
    list_display = ['trade_no', 'process_tag', 'mistake_tag', 'shop_name', 'warehouse_name', 'buyer_nick',
                    'receiver_name', 'receiver_area', 'receiver_address', 'receiver_mobile', 'goods_name', 'spec_code',
                    'num', 'price', 'share_amount', 'pay_time', 'deliver_time', 'logistics_name', 'logistics_no',
                    'buyer_message', 'cs_remark', 'order_status', 'src_tids']
    readonley_fields = ['trade_no', 'process_tag', 'mistake_tag', 'shop_name', 'warehouse_name', 'buyer_nick',
                        'receiver_name', 'receiver_area', 'receiver_address', 'receiver_mobile', 'goods_name',
                        'spec_code', 'num', 'price', 'share_amount', 'pay_time', 'deliver_time', 'logistics_name',
                        'logistics_no', 'buyer_message', 'cs_remark', 'order_status', 'src_tids', 'creator',
                        'is_delete', 'create_time', 'update_time']

    list_filter = ['process_tag', 'mistake_tag', 'trade_no', 'buyer_nick', 'receiver_mobile', 'deliver_time',
                   'goods_name', 'spec_code', 'num', 'price', 'share_amount', 'src_tids', ]

    form_layout = [
        Fieldset('基本信息',
                 Row('shop_name', 'warehouse_name', 'buyer_nick', ),

                 Row('receiver_name', 'receiver_address', 'receiver_mobile', ),
                 Row('goods_name', 'spec_code', 'num',
                     'price', 'share_amount', ),
                 Row('deliver_time', 'logistics_name', 'logistics_no', ), ),
        Fieldset(None,
                 'creator', 'create_time', 'update_time', 'is_delete', **{"style": "display:None"}),
    ]

    def queryset(self):
        queryset = super(PartWHCheckOrderAdmin, self).queryset()
        queryset = queryset.filter(is_delete=0, order_status=2, warehouse_name='中外运苏州配件仓')

        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 配件仓订单查询
class PartWHOrderAdmin(object):
    list_display = ['trade_no', 'process_tag', 'mistake_tag', 'shop_name', 'warehouse_name', 'buyer_nick',
                    'receiver_name', 'receiver_area', 'receiver_address', 'receiver_mobile', 'goods_name', 'spec_code',
                    'num', 'price', 'share_amount', 'pay_time', 'deliver_time', 'logistics_name', 'logistics_no',
                    'buyer_message', 'cs_remark', 'order_status', 'src_tids']
    readonley_fields = ['trade_no', 'process_tag', 'mistake_tag', 'shop_name', 'warehouse_name', 'buyer_nick',
                        'receiver_name', 'receiver_area', 'receiver_address', 'receiver_mobile', 'goods_name',
                        'spec_code', 'num', 'price', 'share_amount', 'pay_time', 'deliver_time', 'logistics_name',
                        'logistics_no', 'buyer_message', 'cs_remark', 'order_status', 'src_tids', 'creator',
                        'is_delete', 'create_time', 'update_time']

    list_filter = ['create_time', 'shop_name', 'goods_name', 'process_tag', 'mistake_tag', 'trade_no', 'buyer_nick',
                   'receiver_mobile', 'deliver_time', 'spec_code', 'num', 'price', 'share_amount', 'src_tids', ]

    actions = [CreatePWSAction]

    form_layout = [
        Fieldset('基本信息',
                 Row('shop_name', 'warehouse_name', 'buyer_nick', ),

                 Row('receiver_name', 'receiver_address', 'receiver_mobile', ),
                 Row('goods_name', 'spec_code', 'num',
                     'price', 'share_amount', ),
                 Row('deliver_time', 'logistics_name', 'logistics_no', ), ),
        Fieldset(None,
                 'creator', 'create_time', 'update_time', 'is_delete', **{"style": "display:None"}),
    ]

    def queryset(self):
        queryset = super(PartWHOrderAdmin, self).queryset()
        queryset = queryset.filter(is_delete=0, warehouse_name='中外运苏州配件仓')

        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 整机仓未关联订单
class MachineWHCheckOrderAdmin(object):
    list_display = ['trade_no', 'process_tag', 'mistake_tag', 'shop_name', 'warehouse_name', 'buyer_nick',
                    'receiver_name', 'receiver_area', 'receiver_address', 'receiver_mobile', 'goods_name', 'spec_code',
                    'num', 'price', 'share_amount', 'pay_time', 'deliver_time', 'logistics_name', 'logistics_no',
                    'buyer_message', 'cs_remark', 'order_status', 'src_tids']
    readonley_fields = ['trade_no', 'process_tag', 'mistake_tag', 'shop_name', 'warehouse_name', 'buyer_nick',
                        'receiver_name', 'receiver_area', 'receiver_address', 'receiver_mobile', 'goods_name',
                        'spec_code', 'num', 'price', 'share_amount', 'pay_time', 'deliver_time', 'logistics_name',
                        'logistics_no', 'buyer_message', 'cs_remark', 'order_status', 'src_tids', 'creator',
                        'is_delete', 'create_time', 'update_time']

    list_filter = ['process_tag', 'mistake_tag', 'trade_no', 'buyer_nick', 'receiver_mobile', 'deliver_time',
                   'goods_name', 'spec_code', 'num', 'price', 'share_amount', 'src_tids', ]

    form_layout = [
        Fieldset('基本信息',
                 Row('shop_name', 'warehouse_name', 'buyer_nick', ),

                 Row('receiver_name', 'receiver_address', 'receiver_mobile', ),
                 Row('goods_name', 'spec_code', 'num',
                     'price', 'share_amount', ),
                 Row('deliver_time', 'logistics_name', 'logistics_no', ), ),
        Fieldset(None,
                 'creator', 'create_time', 'update_time', 'is_delete', **{"style": "display:None"}),
    ]

    def queryset(self):
        queryset = super(MachineWHCheckOrderAdmin, self).queryset()
        queryset = queryset.filter(is_delete=0, order_status=2, warehouse_name='中外运苏州成品仓')

        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 整机仓订单查询
class MachineWHOrderAdmin(object):
    list_display = ['trade_no', 'process_tag', 'mistake_tag', 'shop_name', 'warehouse_name', 'buyer_nick',
                    'receiver_name', 'receiver_area', 'receiver_address', 'receiver_mobile', 'goods_name', 'spec_code',
                    'num', 'price', 'share_amount', 'pay_time', 'deliver_time', 'logistics_name', 'logistics_no',
                    'buyer_message', 'cs_remark', 'order_status', 'src_tids']
    readonley_fields = ['trade_no', 'process_tag', 'mistake_tag', 'shop_name', 'warehouse_name', 'buyer_nick',
                        'receiver_name', 'receiver_area', 'receiver_address', 'receiver_mobile', 'goods_name',
                        'spec_code', 'num', 'price', 'share_amount', 'pay_time', 'deliver_time', 'logistics_name',
                        'logistics_no', 'buyer_message', 'cs_remark', 'order_status', 'src_tids', 'creator',
                        'is_delete', 'create_time', 'update_time']

    list_filter = ['create_time', 'shop_name', 'goods_name', 'process_tag', 'mistake_tag', 'trade_no', 'buyer_nick',
                   'receiver_mobile', 'deliver_time', 'spec_code', 'num', 'price', 'share_amount', 'src_tids', ]

    actions = [CreateGWSAction]

    form_layout = [
        Fieldset('基本信息',
                 Row('shop_name', 'warehouse_name', 'buyer_nick', ),

                 Row('receiver_name', 'receiver_address', 'receiver_mobile', ),
                 Row('goods_name', 'spec_code', 'num',
                     'price', 'share_amount', ),
                 Row('deliver_time', 'logistics_name', 'logistics_no', ), ),
        Fieldset(None,
                 'creator', 'create_time', 'update_time', 'is_delete', **{"style": "display:None"}),
    ]

    def queryset(self):
        queryset = super(MachineWHOrderAdmin, self).queryset()
        queryset = queryset.filter(is_delete=0, warehouse_name='中外运苏州成品仓')

        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 中央仓未关联订单
class CenterTWHCheckOrderAdmin(object):
    list_display = ['trade_no', 'process_tag', 'mistake_tag', 'shop_name', 'warehouse_name', 'buyer_nick',
                    'receiver_name', 'receiver_area', 'receiver_address', 'receiver_mobile', 'goods_name', 'spec_code',
                    'num', 'price', 'share_amount', 'pay_time', 'deliver_time', 'logistics_name', 'logistics_no',
                    'buyer_message', 'cs_remark', 'order_status', 'src_tids']
    readonley_fields = ['trade_no', 'process_tag', 'mistake_tag', 'shop_name', 'warehouse_name', 'buyer_nick',
                        'receiver_name', 'receiver_area', 'receiver_address', 'receiver_mobile', 'goods_name',
                        'spec_code', 'num', 'price', 'share_amount', 'pay_time', 'deliver_time', 'logistics_name',
                        'logistics_no', 'buyer_message', 'cs_remark', 'order_status', 'src_tids', 'creator',
                        'is_delete', 'create_time', 'update_time']

    list_filter = ['process_tag', 'mistake_tag', 'trade_no', 'buyer_nick', 'receiver_mobile', 'deliver_time',
                   'goods_name', 'spec_code', 'num', 'price', 'share_amount', 'src_tids', ]

    form_layout = [
        Fieldset('基本信息',
                 Row('shop_name', 'warehouse_name', 'buyer_nick', ),

                 Row('receiver_name', 'receiver_address', 'receiver_mobile', ),
                 Row('goods_name', 'spec_code', 'num',
                     'price', 'share_amount', ),
                 Row('deliver_time', 'logistics_name', 'logistics_no', ), ),
        Fieldset(None,
                 'creator', 'create_time', 'update_time', 'is_delete', **{"style": "display:None"}),
    ]

    def queryset(self):
        queryset = super(CenterTWHCheckOrderAdmin, self).queryset()
        queryset = queryset.filter(is_delete=0, order_status=2, warehouse_name='中央转运调度仓')

        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 中央仓订单查询
class CenterTWHOrderAdmin(object):
    list_display = ['trade_no', 'process_tag', 'mistake_tag', 'shop_name', 'warehouse_name', 'buyer_nick',
                    'receiver_name', 'receiver_area', 'receiver_address', 'receiver_mobile', 'goods_name', 'spec_code',
                    'num', 'price', 'share_amount', 'pay_time', 'deliver_time', 'logistics_name', 'logistics_no',
                    'buyer_message', 'cs_remark', 'order_status', 'src_tids']
    readonley_fields = ['trade_no', 'process_tag', 'mistake_tag', 'shop_name', 'warehouse_name', 'buyer_nick',
                        'receiver_name', 'receiver_area', 'receiver_address', 'receiver_mobile', 'goods_name',
                        'spec_code', 'num', 'price', 'share_amount', 'pay_time', 'deliver_time', 'logistics_name',
                        'logistics_no', 'buyer_message', 'cs_remark', 'order_status', 'src_tids', 'creator',
                        'is_delete', 'create_time', 'update_time']

    list_filter = ['process_tag', 'mistake_tag', 'trade_no', 'buyer_nick', 'receiver_mobile', 'deliver_time',
                   'goods_name', 'spec_code', 'num', 'price', 'share_amount', 'src_tids', ]

    form_layout = [
        Fieldset('基本信息',
                 Row('shop_name', 'warehouse_name', 'buyer_nick', ),

                 Row('receiver_name', 'receiver_address', 'receiver_mobile', ),
                 Row('goods_name', 'spec_code', 'num',
                     'price', 'share_amount', ),
                 Row('deliver_time', 'logistics_name', 'logistics_no', ), ),
        Fieldset(None,
                 'creator', 'create_time', 'update_time', 'is_delete', **{"style": "display:None"}),
    ]

    def queryset(self):
        queryset = super(CenterTWHOrderAdmin, self).queryset()
        queryset = queryset.filter(is_delete=0, warehouse_name='中央转运调度仓')

        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 尾货订单查询
class TailShopOrderAdmin(object):
    list_display = ['trade_no', 'process_tag', 'mistake_tag', 'shop_name', 'warehouse_name', 'buyer_nick',
                    'receiver_name', 'receiver_area', 'receiver_address', 'receiver_mobile', 'goods_name', 'spec_code',
                    'num', 'pay_time', 'deliver_time', 'logistics_name', 'logistics_no',
                    'buyer_message', 'cs_remark', 'order_status', 'src_tids']
    readonley_fields = ['trade_no', 'process_tag', 'mistake_tag', 'shop_name', 'warehouse_name', 'buyer_nick',
                        'receiver_name', 'receiver_area', 'receiver_address', 'receiver_mobile', 'goods_name',
                        'spec_code', 'num', 'price', 'share_amount', 'pay_time', 'deliver_time', 'logistics_name',
                        'logistics_no', 'buyer_message', 'cs_remark', 'order_status', 'src_tids', 'creator',
                        'is_delete', 'create_time', 'update_time']
    list_exclude = ['price', 'share_amount', ]

    list_filter = ['buyer_nick', 'receiver_mobile', 'deliver_time', 'goods_name', 'spec_code', 'num',
                   'src_tids', ]

    form_layout = [
        Fieldset('基本信息',
                 Row('shop_name', 'warehouse_name', 'buyer_nick', ),

                 Row('receiver_name', 'receiver_address', 'receiver_mobile', ),
                 Row('goods_name', 'spec_code', 'num',),
                 Row('deliver_time', 'logistics_name', 'logistics_no', ), ),
        Fieldset(None,
                 'price', 'share_amount', 'creator', 'create_time', 'update_time',
                 'is_delete', **{"style": "display:None"}),
    ]

    batch_data = True
    nick_ids = []

    def post(self, request, *args, **kwargs):
        ids = request.POST.get('ids', None)
        if ids is not None:
            if " " in ids:
                ids = ids.split(" ")
                self.nick_ids = []
                self.nick_ids = ids
                self.queryset()
            else:
                self.nick_ids = []
                self.nick_ids.append(str(ids).replace("/t", "").replace("/n", "").replace(" ", ""))
                self.queryset()

        return super(TailShopOrderAdmin, self).post(request, *args, **kwargs)

    def queryset(self):
        queryset = super(TailShopOrderAdmin, self).queryset().filter(shop_name='小狗尾货')

        if self.nick_ids:
            queryset = queryset.filter(is_delete=0, receiver_mobile__in=self.nick_ids)
        else:
            queryset = queryset.filter(id=0)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


class SubmitOBMSOrderAdmin(object):
    list_display = ['trade_no', 'process_tag', 'mistake_tag', 'shop_name', 'warehouse_name', 'buyer_nick',
                    'receiver_name', 'province', 'city', 'district', 'street', 'receiver_address',
                    'receiver_mobile', 'goods_name', 'spec_code', 'ori_order_status', 'goods_weight',
                    'num', 'price', 'share_amount', 'pay_time', 'logistics_name', 'logistics_no',
                    'cs_remark', 'order_status', 'src_tids']

    list_filter = ['trade_no', 'process_tag', 'mistake_tag', 'buyer_nick', 'receiver_mobile',
                   'goods_name', 'spec_code', 'num', 'price', 'share_amount', 'src_tids', 'creator']
    actions = [CorrectionODAction]

    form_layout = [
        Fieldset('基本信息',
                 Row('shop_name', 'warehouse_name', 'buyer_nick', ),

                 Row('receiver_name', 'receiver_address', 'receiver_mobile', ),
                 Row('goods_name', 'spec_code', 'num',
                     'price', 'share_amount', ),
                 Row('deliver_time', 'logistics_name', 'logistics_no', ), ),
        Fieldset(None,
                 'creator', 'create_time', 'update_time', 'is_delete', **{"style": "display:None"}),
    ]
    ALLOWED_EXTENSIONS = ['xls', 'xlsx']
    INIT_FIELDS_DIC = {
        "系统单号": "trade_no",
        "店铺名称": "shop_name",
        "仓库名称": "warehouse_name",
        "支付时间": "pay_time",
        "订单类型": "order_category",
        "状态": "ori_order_status",
        "交易订单号": "src_tids",
        "快递公司": "logistics_name",
        "运单号": "logistics_no",
        "买家昵称": "buyer_nick",
        "收货人姓名": "receiver_name",
        "省": "province",
        "市": "city",
        "区": "district",
        "街道": "street",
        "收货人地址": "receiver_address",
        "手机": "receiver_mobile",
        "订单金额": "price",
        "卖家备注": "cs_remark",
        "订货数量": "num",
        "商品小计": "share_amount",
        "商品编码": "spec_code",
        "商品名称": "goods_name",
        "商品重量(克)": "goods_weight",
    }

    import_data = True

    def post(self, request, *args, **kwargs):

        file = request.FILES.get('file', None)
        if file:
            result = self.handle_upload_file(request, file)
            self.message_user('结果提示：%s' % result)
        return super(SubmitOBMSOrderAdmin, self).post(request, *args, **kwargs)

    def handle_upload_file(self, request, _file):
        report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error": []}
        if '.' in _file.name and _file.name.rsplit('.')[-1] in self.__class__.ALLOWED_EXTENSIONS:
            df = pd.read_excel(_file, sheet_name=0, dtype=str)

            FILTER_FIELDS = ['店铺名称', '仓库名称', '支付时间', '订单类型', '状态', '交易订单号',
                             '快递公司', '运单号', '买家昵称', '收货人姓名', '省', '市', '区', '街道',
                             '收货人地址', '手机', '订单金额', '卖家备注', '订货数量', '商品小计', '商品编码',
                             '商品名称', '商品重量(克)', '系统单号']

            try:
                df = df[FILTER_FIELDS]
            except Exception as e:
                report_dic["error"].append(e)
                return report_dic

            # 获取表头，对表头进行转换成数据库字段名
            columns_key = df.columns.values.tolist()
            for i in range(len(columns_key)):
                if self.__class__.INIT_FIELDS_DIC.get(columns_key[i], None) is not None:
                    columns_key[i] = self.__class__.INIT_FIELDS_DIC.get(columns_key[i])

            # 验证一下必要的核心字段是否存在
            _ret_verify_field = OriBMSOrderInfo.verify_mandatory(columns_key)
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

        else:
            report_dic["error"].append('只支持excel文件格式！')
            return report_dic

    @staticmethod
    def save_resources(request, resource):
        # 设置初始报告
        report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error": []}

        for row in resource:
            try:
                _q_trade_no = OriBMSOrderInfo.objects.get(trade_no__exact=row['trade_no'])
                report_dic["repeated"] += 1
                continue
            except OriBMSOrderInfo.DoesNotExist:
                pass
            emo_fields = ['buyer_nick', 'receiver_name', 'receiver_address', 'cs_remark']
            for word in emo_fields:
                row[word] = emoji.demojize(str(row[word]))

            order_fields = ['trade_no', 'shop_name', 'warehouse_name', 'pay_time',
                            'order_category', 'ori_order_status', 'src_tids',
                            'logistics_name', 'logistics_no', 'buyer_nick', 'receiver_name',
                            'province', 'city', 'district', 'street', 'receiver_address', 'receiver_mobile',
                            'price', 'cs_remark', 'num', 'share_amount', 'spec_code', 'goods_name', 'goods_weight']
            order = OriBMSOrderInfo()
            for field in order_fields:
                if row[field] in ['nan', 'NaN']:
                    row[field] = ''
                setattr(order, field, row[field])
            if order.pay_time:
                order.pay_time = datetime.datetime.strptime(order.pay_time, '%Y-%m-%d %H:%M:%S')
            try:
                order.creator = request.user.username
                order.save()
                report_dic["successful"] += 1
            except Exception as e:
                report_dic['error'].append(e)
                report_dic["false"] += 1

        return report_dic

    def queryset(self):
        queryset = super(SubmitOBMSOrderAdmin, self).queryset()
        queryset = queryset.filter(order_status=1)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


class OriBMSOrderInfoAdmin(object):
    list_display = ['trade_no', 'process_tag', 'mistake_tag', 'shop_name', 'warehouse_name', 'buyer_nick',
                    'receiver_name', 'province', 'city', 'district', 'street', 'receiver_address',
                    'receiver_mobile', 'goods_name', 'spec_code', 'ori_order_status', 'goods_weight',
                    'num', 'price', 'share_amount', 'pay_time', 'logistics_name', 'logistics_no',
                    'cs_remark', 'order_status', 'src_tids']

    list_filter = ['trade_no', 'process_tag', 'mistake_tag', 'buyer_nick', 'receiver_mobile',
                   'goods_name', 'spec_code', 'num', 'price', 'share_amount', 'src_tids', 'creator']
    actions = []

    form_layout = [
        Fieldset('基本信息',
                 Row('shop_name', 'warehouse_name', 'buyer_nick', ),

                 Row('receiver_name', 'receiver_address', 'receiver_mobile', ),
                 Row('goods_name', 'spec_code', 'num',
                     'price', 'share_amount', ),
                 Row('deliver_time', 'logistics_name', 'logistics_no', ), ),
        Fieldset(None,
                 'creator', 'create_time', 'update_time', 'is_delete', **{"style": "display:None"}),
    ]

    def has_add_permission(self):
        # 禁用添加按钮
        return False


xadmin.site.register(SubmitOriOrder, SubmitOriOrderAdmin)
xadmin.site.register(OriOrderInfo, OriOrderInfoAdmin)

xadmin.site.register(OriOrderList, OriOrderListAdmin)
xadmin.site.register(SimpleOrder, SimpleOrderAdmin)

xadmin.site.register(SubmitOrder, SubmitOrderAdmin)

xadmin.site.register(LabelOptions, LabelOptionsAdmin)

xadmin.site.register(PartWHCheckOrder, PartWHCheckOrderAdmin)
xadmin.site.register(PartWHOrder, PartWHOrderAdmin)
xadmin.site.register(MachineWHCheckOrder, MachineWHCheckOrderAdmin)
xadmin.site.register(MachineWHOrder, MachineWHOrderAdmin)
xadmin.site.register(CenterTWHCheckOrder, CenterTWHCheckOrderAdmin)
xadmin.site.register(CenterTWHOrder, CenterTWHOrderAdmin)

xadmin.site.register(CheckOrder, CheckOrderAdmin)
xadmin.site.register(OrderInfo, OrderInfoAdmin)

xadmin.site.register(TailShopOrder, TailShopOrderAdmin)
xadmin.site.register(SubmitOBMSOrder, SubmitOBMSOrderAdmin)
xadmin.site.register(OriBMSOrderInfo, OriBMSOrderInfoAdmin)