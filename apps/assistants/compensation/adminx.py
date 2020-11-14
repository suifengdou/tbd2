# -*- coding: utf-8 -*-
# @Time    : 2020/9/15 10:53
# @Author  : Hann
# @Site    : 
# @File    : adminx.py
# @Software: PyCharm

import math, re
import datetime
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

from .models import OCCheck, OriCompensation, CCheck, Compensation, OriToCList, BCheck, BatchCompensation, BatchInfo, BSubmit, BICheck


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
                if isinstance(obj, OriCompensation):
                    if obj.order_status > 0:
                        obj.order_status -= 1
                        obj.process_tag = 0
                        obj.save()
                        if obj.order_status == 0:
                            self.message_user("%s 取消成功" % obj.order_id, "success")
                        else:
                            self.message_user("%s 驳回上一级成功" % obj.order_id, "success")
                    else:
                        n -= 1
                        self.message_user("%s 单据状态错误，请检查，驳回出错。" % obj.order_id, "error")
                if isinstance(obj, Compensation):
                    if obj.order_status > 0:
                        obj.order_status -= 1
                        obj.save()
                        _q_list_order = OriToCList.objects.filter(order=obj, order_status=1)
                        for list_order in _q_list_order:
                            list_order.order_status = 0
                            list_order.save()
                            list_order.ori_order.order_status = 1
                            list_order.ori_order.save()
                        if obj.order_status == 0:
                            self.message_user("%s 取消成功" % obj.order_id, "success")
                        else:
                            self.message_user("%s 驳回上一级成功" % obj.order_id, "success")

                    else:
                        n -= 1
                        self.message_user("%s 单据状态错误，请检查，驳回出错。" % obj.order_id, "error")
                if isinstance(obj, BatchCompensation):
                    if obj.order_status > 0:
                        obj.order_status -= 1
                        obj.save()
                        if obj.order_status == 0:
                            info_orders = obj.batchinfo_set.all()
                            for order in info_orders:
                                order.compensation_order.order_status = 1
                                order.compensation_order.save()
                            info_orders.delete()
                            self.message_user("%s 取消成功" % obj.order_id, "success")
                        else:
                            info_orders = obj.batchinfo_set.all()
                            info_orders.update(process_tag=0)
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


# 设置为特殊类型补偿单
class SetSpecialAction(BaseActionView):
    action_name = "set_special"
    description = "设置特殊类型"
    model_perm = 'change'
    icon = "fa fa-check-square-o"

    @filter_hook
    def do_action(self, queryset):
        if not self.has_change_permission():
            raise PermissionDenied
        n = queryset.count()
        if n:
            self.log('change',
                     '批量设置了 %(count)d %(items)s.' % {"count": n, "items": model_ngettext(self.opts, n)})
            queryset.update(process_tag=5)

            self.message_user("成功设置 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


# 设置为特殊类型补偿单
class SetRecoverAction(BaseActionView):
    action_name = "set_recover"
    description = "设置重置"
    model_perm = 'change'
    icon = "fa fa-check-square-o"

    @filter_hook
    def do_action(self, queryset):
        if not self.has_change_permission():
            raise PermissionDenied
        n = queryset.count()
        if n:
            self.log('change',
                     '批量设置了 %(count)d %(items)s.' % {"count": n, "items": model_ngettext(self.opts, n)})
            queryset.update(process_tag=6)

            self.message_user("成功设置 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


# 原始补偿单提交
class SubmitOCAction(BaseActionView):
    action_name = "submit_occ"
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
                    _attr_fileds = ['servicer', 'shop', 'goods_name', 'nickname', 'order_id', 'compensation',
                                    'name', 'alipay_id', 'actual_receipts', 'receivable', 'checking', 'creator']
                    recover_tag = 0
                    if obj.process_tag == 6:
                        OriToCList.objects.filter(ori_order=obj).delete()
                    _q_repeated_order = OriToCList.objects.filter(ori_order=obj, order_status=1)
                    if _q_repeated_order.exists():
                            self.message_user("%s 重复提交的订单" % obj.order_id, "error")
                            obj.mistake_tag = 1
                            obj.save()
                            n -= 1
                            continue
                    _q_order_id = OriCompensation.objects.filter(order_id=obj.order_id)
                    if len(_q_order_id) > 1:
                        if obj.process_tag != 5:
                            self.message_user("%s 相同单号存在多个差价，需要设置特殊订单" % obj.order_id, "error")
                            obj.mistake_tag = 8
                            obj.save()
                            n -= 1
                            continue
                    _q_recover_order = OriToCList.objects.filter(ori_order=obj, order_status=0)
                    if _q_recover_order.exists():
                        recover_ori2com_order = _q_recover_order[0]
                        recover_ori2com_order.order_status = 1

                        recover_order = recover_ori2com_order.order
                        if recover_order.order_status == 0:
                            for attr in _attr_fileds:
                                if hasattr(recover_order, attr):
                                    setattr(recover_order, attr, getattr(obj, attr))
                            if recover_order.actual_receipts - recover_order.receivable != recover_order.checking:
                                self.message_user("%s 实收减应收不等于校验金额" % obj.order_id, "error")
                                obj.mistake_tag = 4
                                obj.save()
                                n -= 1
                                continue
                            if recover_order.checking != recover_order.compensation:
                                self.message_user("%s 差价金额不等于校验金额" % obj.order_id, "error")
                                obj.mistake_tag = 5
                                obj.save()
                                n -= 1
                                continue
                            try:
                                recover_order.memorandum = '恢复类型'
                                recover_order.order_status = 1
                                recover_order.creator = self.request.user.username
                                recover_ori2com_order.creator = self.request.user.username
                                recover_order.save()
                                recover_ori2com_order.save()
                                recover_tag = 1
                            except Exception as e:
                                self.message_user("%s 恢复单保存出错:%s" % (obj.order_id, e), "error")
                                obj.mistake_tag = 6
                                obj.save()
                                n -= 1
                                continue
                        elif recover_order.order_status == 1:
                            recover_order.compensation += obj.compensation
                            recover_order.order_id = "%s,%s" % (recover_order.order_id, obj.order_id)
                            recover_order.actual_receipts += obj.actual_receipts
                            recover_order.receivable += obj.receivable
                            recover_order.checking += obj.checking
                            recover_order.memorandum = "%s追加订单号：%s +" % (recover_order.memorandum, obj.order_id)

                            try:
                                recover_ori2com_order.creator = self.request.user.username
                                recover_order.save()
                                recover_ori2com_order.ori_order = obj
                                recover_ori2com_order.order = recover_order
                                recover_ori2com_order.save()
                                recover_tag = 1
                            except Exception as e:
                                self.message_user("%s 追加单保存出错:%s" % (obj.order_id, e), "error")
                                obj.mistake_tag = 3
                                obj.save()
                                n -= 1
                                continue
                        else:
                            self.message_user("%s 恢复订单出错，需要设置订单为重置" % obj.order_id, "error")
                            obj.mistake_tag = 9
                            obj.save()
                            n -= 1
                            continue
                    if not recover_tag:
                        _q_add_order = Compensation.objects.filter(name=obj.name, alipay_id=obj.alipay_id, order_status=1)
                        if _q_add_order.exists():
                            if obj.process_tag != 5:
                                self.message_user("%s 必须是特殊订单才能追加" % obj.order_id, "error")
                                obj.mistake_tag = 2
                                obj.save()
                                n -= 1
                                continue
                            add_order = _q_add_order[0]
                            add_order.compensation += obj.compensation
                            add_order.order_id = "%s,%s" % (add_order.order_id, obj.order_id)
                            add_order.actual_receipts += obj.actual_receipts
                            add_order.receivable += obj.receivable
                            add_order.checking += obj.checking
                            add_order.memorandum = "%s追加订单号：%s +" % (add_order.memorandum, obj.order_id)
                            add_ori2com_order = OriToCList()

                            try:
                                add_ori2com_order.creator = self.request.user.username
                                add_order.save()
                                add_ori2com_order.ori_order = obj
                                add_ori2com_order.order = add_order
                                add_ori2com_order.save()
                            except Exception as e:
                                self.message_user("%s 追加单保存出错:%s" % (obj.order_id, e), "error")
                                obj.mistake_tag = 3
                                obj.save()
                                n -= 1
                                continue
                        else:
                            com_order = Compensation()
                            ori2com_order = OriToCList()
                            for attr in _attr_fileds:
                                if hasattr(com_order, attr):
                                    setattr(com_order, attr, getattr(obj, attr))
                            if com_order.actual_receipts - com_order.receivable != com_order.checking:
                                self.message_user("%s 实收减应收不等于校验金额" % obj.order_id, "error")
                                obj.mistake_tag = 4
                                obj.save()
                                n -= 1
                                continue
                            if com_order.checking != com_order.compensation:
                                self.message_user("%s 差价金额不等于校验金额" % obj.order_id, "error")
                                obj.mistake_tag = 5
                                obj.save()
                                n -= 1
                                continue
                            try:

                                ori2com_order.creator = self.request.user.username
                                com_order.save()
                                ori2com_order.ori_order = obj
                                ori2com_order.order = com_order
                                ori2com_order.save()
                            except Exception as e:
                                self.message_user("%s 补偿单保存出错:%s" % (obj.order_id, e), "error")
                                obj.mistake_tag = 7
                                obj.save()
                                n -= 1
                                continue

                    obj.submit_time = datetime.datetime.now()
                    obj.handler = self.request.user.username
                    obj.order_status = 2
                    obj.mistake_tag = 0
                    obj.process_tag = 4
                    obj.save()

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


# 补偿单提交
class SubmitCAction(BaseActionView):
    action_name = "submit_c"
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

                prefix = "BC"
                serial_number = str(datetime.datetime.now())
                serial_number = str(serial_number.replace("-", "").replace(" ", "").replace(":", "").replace(".", ""))
                batch_order = BatchCompensation()
                batch_order.order_id = prefix + serial_number
                batch_order.quantity = queryset.count()
                try:
                    batch_order.creator = self.request.user.username
                    batch_order.save()
                except Exception as e:
                    self.message_user("汇总单保存出错:%s" % e, "error")
                    queryset.update(mistake_tag=1)
                    return None
                for obj in queryset:
                    self.log('change', '', obj)
                    _attr_fileds = ['servicer', 'shop', 'goods_name', 'nickname', 'order_id', 'compensation',
                                    'name', 'alipay_id', 'actual_receipts', 'receivable', 'checking', 'creator']
                    batch_info_order = BatchInfo()
                    for attr in _attr_fileds:
                        if hasattr(batch_info_order, attr):
                            setattr(batch_info_order, attr, getattr(obj, attr))
                    batch_info_order.compensation_order = obj
                    batch_info_order.paid_amount = obj.compensation
                    batch_info_order.batch_order = batch_order
                    try:
                        batch_info_order.save()
                    except Exception as e:
                        self.message_user("%s 汇总单明细保存出错:%s" % (obj.order_id, e), "error")
                        obj.mistake_tag = 2
                        obj.save()
                        n -= 1
                        continue
                    obj.submit_time = datetime.datetime.now()
                    obj.handler = self.request.user.username
                    obj.order_status = 2
                    obj.mistake_tag = 0
                    obj.process_tag = 0
                    obj.save()

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


# 补偿单提交
class SubmitBCAction(BaseActionView):
    action_name = "submit_bc"
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
                    if not obj.oa_order_id:
                        self.message_user("%s 无OA单号" % obj.order_id, "error")
                        obj.mistake_tag = 1
                        obj.save()
                        n -= 1
                        continue
                    _q_oa_order_q = BatchCompensation.objects.filter(oa_order_id=obj.oa_order_id)
                    if len(_q_oa_order_q) > 1:
                        self.message_user("%s 已递交过此OA单号" % obj.oa_order_id, "error")
                        obj.mistake_tag = 3
                        obj.save()
                        n -= 1
                        continue
                    obj.order_status = 2
                    obj.batchinfo_set.all().update(process_tag=2)
                    obj.mistake_tag = 0
                    obj.process_tag = 2
                    obj.save()

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


# 设置为特殊类型补偿单
class SetFinishAction(BaseActionView):
    action_name = "set_finished"
    description = "设置为已完成"
    model_perm = 'change'
    icon = "fa fa-check-square-o"

    @filter_hook
    def do_action(self, queryset):
        if not self.has_change_permission():
            raise PermissionDenied
        n = queryset.count()
        if n:
            self.log('change',
                     '批量设置了 %(count)d %(items)s.' % {"count": n, "items": model_ngettext(self.opts, n)})
            queryset.update(process_tag=4)

            self.message_user("成功设置 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


# 补偿单审核
class CheckBCAction(BaseActionView):
    action_name = "check_bc"
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
                    if obj.process_tag != 4:
                        self.message_user("%s 先设置订单已完成再审核" % obj.order_id, "error")
                        obj.mistake_tag = 2
                        obj.save()
                        n -= 1
                        continue
                    obj.order_status = 3
                    info_order = obj.batchinfo_set.all()
                    info_order.update(process_tag=4)
                    for order in info_order:
                        if order.paid_amount:
                            order.compensation_order.process_tag = 4
                            order.compensation_order.save()
                    obj.handle_time = datetime.datetime.now()
                    obj.handler = self.request.user.username
                    obj.mistake_tag = 0
                    obj.process_tag = 4
                    obj.save()

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


# 财务重置补尝单
class RecoveBIAction(BaseActionView):
    action_name = "recove_bi"
    description = "重置补尝单"
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
                    if obj.paid_amount:
                        self.message_user("%s 已付金额不是零，不可重置" % obj.order_id, "error")
                        obj.mistake_tag = 1
                        obj.save()
                        n -= 1
                        continue
                    self.log('change', '', obj)
                    _attr_fileds = ['servicer', 'shop', 'goods_name', 'nickname', 'order_id', 'compensation',
                                    'name', 'alipay_id', 'actual_receipts', 'receivable', 'checking', 'creator']
                    new_order = OriCompensation()
                    for attr in _attr_fileds:
                        if hasattr(new_order, attr):
                            setattr(new_order, attr, getattr(obj, attr))
                    try:
                        new_order.order_category = 2
                        new_order.memorandum = '错误的单据，于%s财务重置创建' % self.request.user.username
                        new_order.save()
                    except Exception as e:
                        self.message_user("%s 重置保存补偿单出错:%s" % (obj.order_id, e), "error")
                        obj.mistake_tag = 2
                        obj.save()
                        n -= 1
                        continue
                    obj.process_tag = 4
                    obj.mistake_tag = 0
                    obj.save()

            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')

        return None


class OCCheckAdmin(object):
    list_display = ['servicer', 'process_tag', 'mistake_tag', 'shop', 'goods_name', 'nickname', 'order_id',
                    'order_category', 'compensation','name', 'alipay_id', 'actual_receipts', 'receivable',
                    'checking', 'memorandum']
    list_filter = ['servicer', 'process_tag', 'mistake_tag', 'shop', 'goods_name', 'nickname', 'order_id',
                   'order_category', 'compensation', 'name', 'alipay_id', 'memorandum']
    search_fields = []
    list_editable = ['compensation', 'alipay_id', 'name', 'actual_receipts', 'receivable', 'checking',]
    actions = [SetRecoverAction, SetSpecialAction, SubmitOCAction, RejectSelectedAction]
    readonly_fields = []
    form_layout = [
        Fieldset('基本信息',
                 Row('shop', 'nickname',),
                 Row('order_id', 'order_category',),
                 Row('goods_name', 'alipay_id',),
                 Row('compensation',),),
        Fieldset('验算信息',
                 Row('actual_receipts', 'receivable', 'checking',),),
        Fieldset(None,
                 'process_tag', 'mistake_tag', 'order_status', 'is_delete', 'creator',
                 **{"style": "display:None"}),
    ]

    def queryset(self):
        queryset = super(OCCheckAdmin, self).queryset()
        queryset = queryset.filter(order_status=1, is_delete=0)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


class OriCompensationAdmin(object):
    list_display = ['servicer', 'process_tag', 'mistake_tag', 'shop', 'goods_name', 'nickname', 'order_id',
                    'order_category', 'compensation', 'name', 'alipay_id', 'actual_receipts', 'receivable',
                    'checking', 'memorandum']
    list_filter = ['servicer', 'process_tag', 'mistake_tag', 'shop', 'goods_name', 'nickname', 'order_id',
                   'order_category', 'compensation', 'name', 'alipay_id', 'memorandum']
    search_fields = []
    readonly_fields = ['servicer', 'process_tag', 'mistake_tag', 'shop', 'goods_name', 'nickname', 'order_id',
                       'order_category', 'compensation', 'name', 'alipay_id', 'actual_receipts', 'receivable',
                       'checking', 'memorandum']
    form_layout = [
        Fieldset('基本信息',
                 Row('shop', 'nickname', 'order_status',),
                 Row('order_id', 'order_category', ),
                 Row('goods_name', 'alipay_id', ),
                 Row('compensation', ), ),
        Fieldset('验算信息',
                 Row('actual_receipts', 'receivable', 'checking', ), ),
        Fieldset(None,
                 'process_tag', 'mistake_tag', 'is_delete', 'creator',
                 **{"style": "display:None"}),
    ]
    def has_add_permission(self):
        # 禁用添加按钮
        return False


class CCheckAdmin(object):
    list_display = ['servicer', 'process_tag', 'mistake_tag', 'shop', 'goods_name', 'nickname', 'order_id',
                    'compensation', 'name', 'alipay_id', 'actual_receipts', 'receivable',
                    'checking', 'memorandum']
    list_filter = ['servicer', 'process_tag', 'mistake_tag', 'shop', 'goods_name', 'nickname', 'order_id',
                   'compensation', 'name', 'alipay_id', 'memorandum']
    search_fields = []
    readonly_fields = ['servicer', 'process_tag', 'mistake_tag', 'shop', 'goods_name', 'nickname', 'order_id',
                       'compensation', 'name', 'alipay_id', 'actual_receipts', 'receivable',
                       'checking', 'memorandum', 'handler', 'handle_time', 'order_status', 'creator', 'is_delete']
    actions = [SubmitCAction, RejectSelectedAction,]

    def queryset(self):
        queryset = super(CCheckAdmin, self).queryset()
        queryset = queryset.filter(order_status=1, is_delete=0)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


class CompensationAdmin(object):
    list_display = ['servicer', 'order_status', 'process_tag', 'mistake_tag', 'shop', 'goods_name', 'nickname',
                    'order_id', 'compensation', 'name', 'alipay_id', 'actual_receipts', 'receivable', 'update_time',
                    'checking', 'memorandum']
    list_filter = ['servicer', 'process_tag', 'mistake_tag', 'shop', 'goods_name', 'nickname', 'order_id',
                   'compensation', 'name', 'alipay_id', 'memorandum', 'creator', 'create_time']
    search_fields = []
    readonly_fields = ['servicer', 'process_tag', 'mistake_tag', 'shop', 'goods_name', 'nickname', 'order_id',
                       'compensation', 'name', 'alipay_id', 'actual_receipts', 'receivable',
                       'checking', 'memorandum', 'handler', 'handle_time', 'order_status', 'creator', 'is_delete']

    def has_add_permission(self):
        # 禁用添加按钮
        return False


class OriToCListAdmin(object):
    def has_add_permission(self):
        # 禁用添加按钮
        return False


class BCInfoInline(object):
    model = BatchInfo
    exclude = ['is_delete']

    extra = 1
    style = 'table'


class BSubmitAdmin(object):
    list_display = ['order_id', 'mistake_tag', 'process_tag', 'oa_order_id', 'amount', 'quantity', 'creator']
    list_filter = ['mistake_tag', 'process_tag', 'quantity', 'oa_order_id', 'creator']
    readonly_fields = ['order_id', 'mistake_tag', 'process_tag', 'amount', 'quantity', 'creator']
    list_editable = ['oa_order_id']
    inlines = [BCInfoInline]
    actions = [SubmitBCAction, RejectSelectedAction]
    form_layout = [
        Fieldset('基本信息',
                 Row('order_id', 'creator', ),
                 Row('amount', 'quantity', ),),
        Fieldset(None,
                 'process_tag', 'mistake_tag', 'order_status', 'is_delete', 'handler', 'handle_time',
                 **{"style": "display:None"}),]

    def queryset(self):
        queryset = super(BSubmitAdmin, self).queryset()
        queryset = queryset.filter(order_status=1, is_delete=0)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


class BCheckAdmin(object):
    list_display = ['order_id', 'oa_order_id', 'mistake_tag', 'process_tag', 'amount', 'quantity', 'creator']
    list_filter = ['mistake_tag', 'process_tag', 'quantity', 'oa_order_id', 'creator']
    readonly_fields = ['oa_order_id', 'order_id', 'mistake_tag', 'process_tag', 'amount', 'quantity', 'creator']
    list_editable = ['oa_order_id']
    inlines = [BCInfoInline]
    actions = [SetFinishAction, CheckBCAction]
    form_layout = [
        Fieldset('基本信息',
                 Row('order_id', 'creator', ),
                 Row('amount', 'quantity', ), ),
        Fieldset(None,
                 'process_tag', 'mistake_tag', 'order_status', 'is_delete', 'handler', 'handle_time',
                 **{"style": "display:None"}), ]

    def queryset(self):
        queryset = super(BCheckAdmin, self).queryset()
        queryset = queryset.filter(order_status=2, is_delete=0)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


class BatchCompensationAdmin(object):
    list_display = ['order_id', 'order_status', 'oa_order_id', 'mistake_tag', 'process_tag', 'amount', 'quantity',
                    'handler', 'handle_time', 'creator']
    list_filter = ['mistake_tag', 'process_tag', 'quantity', 'oa_order_id', 'creator']
    readonly_fields = ['oa_order_id', 'order_id', 'mistake_tag', 'process_tag', 'amount', 'quantity', 'creator',
                       'handler', 'handle_time', 'order_status', 'oa_order_id']
    inlines = [BCInfoInline]
    form_layout = [
        Fieldset('基本信息',
                 Row('order_id', 'creator', ),
                 Row('amount', 'quantity', ), ),
        Fieldset(None,
                'mistake_tag', 'is_delete',
                 **{"style": "display:None"}), ]

    def has_add_permission(self):
        # 禁用添加按钮
        return False


class BICheckAdmin(object):
    list_display = ['batch_order', 'mistake_tag', 'process_tag', 'alipay_id', 'name', 'compensation', 'paid_amount',
                    'servicer', 'shop', 'goods_name', 'nickname', 'order_id', 'actual_receipts',
                    'receivable', 'checking', 'oa_order_id', 'compensation_order', ]

    list_filter = ['batch_order__oa_order_id', 'batch_order__order_id', 'alipay_id', 'name', 'process_tag',
                   'compensation', 'paid_amount', 'creator']
    readonly_fields = ['oa_order_id', 'order_id', 'mistake_tag', 'process_tag', 'amount', 'quantity', 'creator',
                       'handler', 'handle_time', 'order_status']
    list_editable = ['paid_amount']
    actions = [RecoveBIAction]
    form_layout = [
        Fieldset('基本信息',
                 Row('batch_order__oa_order_id', 'batch_order__order_id', 'creator'),
                 Row('shop', 'nickname', 'order_id'),
                 Row('alipay_id', 'compensation', 'name'),
                 Row('paid_amount'),
                 ),
        Fieldset(None,
                 'mistake_tag', 'is_delete',
                 **{"style": "display:None"}), ]

    def queryset(self):
        queryset = super(BICheckAdmin, self).queryset()
        queryset = queryset.filter(process_tag=2, is_delete=0)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


class BatchInfoAdmin(object):
    list_display = ['batch_order', 'mistake_tag', 'process_tag', 'alipay_id', 'name', 'compensation', 'paid_amount',
                    'servicer', 'shop', 'goods_name', 'nickname', 'order_id', 'actual_receipts',
                    'receivable', 'checking', 'oa_order_id', 'compensation_order', ]

    list_filter = ['batch_order__oa_order_id', 'batch_order__order_id', 'alipay_id', 'nickname', 'name', 'process_tag',
                   'compensation', 'paid_amount', 'creator']
    readonly_fields = ['oa_order_id', 'order_id', 'mistake_tag', 'process_tag', 'amount', 'quantity', 'creator',
                       'nickname', 'handler', 'handle_time', 'order_status']
    list_editable = ['paid_amount']
    form_layout = [
        Fieldset('基本信息',
                 Row('batch_order__oa_order_id', 'batch_order__order_id', 'creator'),
                 Row('shop', 'nickname', 'order_id'),
                 Row('alipay_id', 'compensation', 'name'),
                 Row('paid_amount'),
                 ),
        Fieldset(None,
                 'mistake_tag', 'is_delete',
                 **{"style": "display:None"}), ]

    def has_add_permission(self):
        # 禁用添加按钮
        return False


xadmin.site.register(OCCheck, OCCheckAdmin)
xadmin.site.register(OriCompensation, OriCompensationAdmin)
xadmin.site.register(CCheck, CCheckAdmin)
xadmin.site.register(Compensation, CompensationAdmin)

xadmin.site.register(OriToCList, OriToCListAdmin)
xadmin.site.register(BSubmit, BSubmitAdmin)
xadmin.site.register(BCheck, BCheckAdmin)
xadmin.site.register(BatchCompensation, BatchCompensationAdmin)
xadmin.site.register(BICheck, BICheckAdmin)
xadmin.site.register(BatchInfo, BatchInfoAdmin)

