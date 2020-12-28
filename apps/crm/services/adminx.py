# -*- coding: utf-8 -*-
# @Time    : 2020/11/22 15:10
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
from django.utils.safestring import mark_safe
from django.contrib.admin.utils import get_deleted_objects

from django.core.files.uploadedfile import InMemoryUploadedFile

import xadmin
from xadmin.plugins.actions import BaseActionView
from xadmin.views.base import filter_hook
from xadmin.util import model_ngettext
from xadmin.layout import Fieldset, Main, Row, Side

from .models import SSICreate, SSIDistribute, SSIProcess, ServicesInfo, SDDistribute
from .models import SDProcess, ServicesDetail, SSIFinished, SDCreate, SDFeedback
from apps.crm.webchatcus.models import WarrantyInfo, WebchatCus
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

                if isinstance(obj, ServicesInfo):
                    details = obj.servicesdetail_set.all().filter(order_status__in=[3, 4])
                    if details.exists():
                        self.message_user("此单据存在被领用过的客户，无法驳回", "error")
                        continue
                    if obj.order_status == 1:
                        obj.order_status -= 1
                    else:
                        obj.order_status = 1
                        details = obj.servicesdetail_set.all()
                        details.update(order_status=1)
                    obj.process_tag = 5
                    if obj.order_status == 0:
                        details = obj.servicesdetail_set.all()
                        details.delete()
                        self.message_user("%s 取消成功" % obj.name, "success")
                    obj.save()

                if isinstance(obj, ServicesDetail):
                    obj.order_status -= 1
                    obj.process_tag = 5
                    obj.handler = ''
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


# 确认关系任务
class ConfirmSSIAction(BaseActionView):
    action_name = "confirm_ssi"
    description = "确认关系任务"
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
                    self.log('change', '%s确认了关系任务' % self.request.user.username, obj)
                    if not obj.services_info:
                        self.message_user("任务说明和要点为必填项", "error")
                        obj.mistake_tag = 1
                        obj.save()
                        continue
                    obj.order_status = 2
                    obj.save()
            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')
        return None


# 提交关系任务
class SubmitSSIAction(BaseActionView):
    action_name = "submit_ssi"
    description = "提交关系任务"
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
                    self.log('change', '%s提交了关系任务' % self.request.user.username, obj)
                    obj.servicesdetail_set.all().update(order_status=2, process_tag=1)
                    obj.order_status = 3
                    obj.save()
            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')
        return None


# 过滤完成的关系任务
class FilterSDAction(BaseActionView):
    action_name = "filter_sd"
    description = "过滤关系任务"
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
                    if not obj.order_type == 2:
                        self.message_user("%s 此任务并不是快捷注册任务" % obj.target, "error")
                        n -= 1
                        continue
                    _q_customer = WebchatCus.objects.filter(customer=obj.customer)
                    if _q_customer.exists():
                        obj.process_tag = 7
                        obj.order_status = 5
                        obj.is_completed = True
                        if not obj.outcome:
                            obj.outcome = 6
                        if not obj.handler:
                            obj.handler = self.request.user.username
                            obj.handle_time = datetime.datetime.now()
                        obj.save()
                        continue
                    if not obj.warranty_sn:
                        n -= 1
                        continue
                    _q_warranty_sn = WarrantyInfo.objects.filter(warranty_sn=obj.warranty_sn)
                    if _q_warranty_sn.exists():
                        obj.process_tag = 7
                        obj.order_status = 5
                        obj.is_completed = True
                        if not obj.outcome:
                            obj.outcome = 6
                        if not obj.handler:
                            obj.handler = self.request.user.username
                            obj.handle_time = datetime.datetime.now()
                        obj.save()
                        continue
            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')
        return None


# 领取关系任务
class GetSDAction(BaseActionView):
    action_name = "get_sd"
    description = "领取关系任务"
    model_perm = 'change'
    icon = "fa fa-flag"

    modify_models_batch = False

    @filter_hook
    def do_action(self, queryset):
        queryset = queryset[:1000]
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
                    self.log('change', '%s提交了关系任务' % self.request.user.username, obj)
                    if obj.handler:
                        self.message_user("%s 此客户已经被领取" % obj.target, "error")
                        continue
                    obj.handler = self.request.user.username
                    obj.process_tag = 2
                    obj.order_status = 3
                    obj.save()
            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')
        return None


# 确认关系任务明细
class ConfirmSDAction(BaseActionView):
    action_name = "confirm_sd"
    description = "确认关系任务"
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
                    self.log('change', '%s提交了关系任务明细' % self.request.user.username, obj)
                    if not obj.handle_time:
                        self.message_user("%s 此客户还未处理，系统没有记录到实施时间" % obj.target, "error")
                        obj.mistake_tag = 1
                        obj.save()
                        continue
                    if not obj.outcome:
                        self.message_user("%s 此客户还未登记处理结果" % obj.target, "error")
                        obj.mistake_tag = 2
                        obj.save()
                        continue
                    obj.mistake_tag = 0
                    obj.process_tag = 4
                    obj.order_status = 4
                    obj.save()
            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')
        return None


# 终审关系任务
class FinishSSIAction(BaseActionView):
    action_name = "finished_ssi_order"
    description = "终审关系任务"
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
                    self.log('change', '%s终审了关系任务明细' % self.request.user.username, obj)
                    obj.mistake_tag = 0
                    obj.process_tag = 4
                    obj.order_status = 5
                    obj.save()
            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')
        return None


# 确认短信关系任务
class FinishMSAction(BaseActionView):
    action_name = "finished_ms_sd"
    description = "完成短信快捷注册任务"
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
                queryset.update(outcome=3, handler=self.request.user.username, handle_time=datetime.datetime.now())
            else:
                for obj in queryset:
                    self.log('change', '%s提交了关系任务明细' % self.request.user.username, obj)
                    if not obj.handle_time:
                        self.message_user("%s 此客户还未处理，系统没有记录到实施时间" % obj.target, "error")
                        obj.mistake_tag = 1
                        obj.save()
                        continue
                    if not obj.outcome:
                        self.message_user("%s 此客户还未登记处理结果" % obj.target, "error")
                        obj.mistake_tag = 2
                        obj.save()
                        continue
                    obj.process_tag = 4
                    obj.order_status = 4
                    obj.save()
            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')
        return None


# 完结旺旺关系任务
class FinishWWAction(BaseActionView):
    action_name = "finished_wangwang_sd"
    description = "终结旺旺留言任务"
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
                queryset.update()
            else:
                for obj in queryset:
                    self.log('change', '%s提交了关系任务明细' % self.request.user.username, obj)
                    if obj.services.order_category != 3:
                        self.message_user("%s 此任务不是旺旺任务无法批量完结" % obj.target, "error")
                        obj.mistake_tag = 3
                        obj.save()
                        continue
                    obj.handler = self.request.user.username
                    obj.handle_time = datetime.datetime.now()
                    obj.is_completed = True
                    obj.process_tag = 4
                    obj.order_status = 5
                    obj.save()
            self.message_user("成功提交 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')
        return None


# 快捷创建注册任务
class CreateRepeatAction(BaseActionView):
    action_name = "create_service_repeat"
    description = "再次创建快捷注册任务"
    model_perm = 'change'
    icon = "fa fa-flag"

    modify_models_batch = False

    @filter_hook
    def do_action(self, queryset):
        queryset = queryset.filter(order_type=2)
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
                service_order.name = str(serial_number) + '重复快捷注册任务-需要改名'
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
                    service_detail.customer = obj.customer
                    service_detail.order_type = service_order.order_type
                    service_detail.services = service_order
                    service_detail.target = obj.customer.mobile
                    service_detail.creator = self.request.user.username
                    service_detail.warranty_sn = obj.warranty_sn
                    service_detail.memorandum = '#来源于 %s ' % str(obj.services.name)
                    try:
                        service_detail.save()
                        obj.order_status = 5
                        obj.save()
                    except Exception as e:
                        self.message_user("保存明细出错：%s" % e, "error")
                        continue
            self.message_user("成功创建 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')
        return None


# 待生成任务
class SSICreateAdmin(object):
    list_display = ['name', 'count_down', 'mistake_tag', 'process_tag', 'order_category', 'order_type',
                    'prepare_time', 'services_info', 'quantity', 'memorandum', 'creator', 'create_time']

    actions = [ConfirmSSIAction, RejectSelectedAction]

    list_filter = ['name', 'mistake_tag', 'process_tag', 'count_down', 'order_category', 'memorandum',
                   'creator', 'create_time']

    form_layout = [
        Fieldset('基本信息',
                 'name', 'order_category','order_type',),
        Fieldset('任务详情',
                 'prepare_time', 'services_info', ),
        Fieldset(None,
                 'process_tag', 'mistake_tag', 'order_status', 'finish_time', 'start_time', 'update_time', 'quantity',
                 'received_num', 'completed_num', 'count_down', 'creator', 'is_delete', **{"style": "display:None"}),
    ]

    ordering = ['name']

    def save_models(self):
        obj = self.new_obj
        all_details = obj.servicesdetail_set.all()
        services_info = obj.services_info
        order_type = obj.order_type
        all_details.update(services_info=services_info, order_type=order_type)
        obj.quantity = all_details.count()
        obj.save()
        super().save_models()

    def queryset(self):
        queryset = super(SSICreateAdmin, self).queryset().filter(order_status=1, is_delete=0)
        for obj in queryset:
            obj.count_down = int((obj.prepare_time - datetime.datetime.now()).days)
            if obj.count_down < 0:
                obj.count_down = 0
            obj.save()
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 待分配任务
class SSIDistributeAdmin(object):
    list_display = ['name', 'count_down', 'mistake_tag', 'process_tag', 'order_category', 'order_type', 'prepare_time',
                    'services_info', 'quantity', 'memorandum', 'creator', 'create_time']

    actions = [SubmitSSIAction, RejectSelectedAction]

    list_filter = ['name', 'mistake_tag', 'process_tag', 'count_down', 'order_category', 'memorandum',
                   'creator', 'create_time']
    readonly_fields = ['id', 'name', 'count_down', 'mistake_tag', 'process_tag', 'order_category', 'prepare_time',
                       'services_info', 'quantity', 'memorandum', 'creator', 'create_time', 'is_delete', 'order_type']
    form_layout = [
        Fieldset('基本信息',
                 'name', 'order_category', 'order_type',),
        Fieldset('任务详情',
                 'prepare_time', 'services_info', ),
        Fieldset(None,
                 'process_tag', 'mistake_tag', 'order_status', 'finish_time', 'start_time', 'update_time', 'quantity',
                 'received_num', 'completed_num', 'count_down', 'creator', 'is_delete', **{"style": "display:None"}),
    ]

    ordering = ['count_down']

    def queryset(self):
        queryset = super(SSIDistributeAdmin, self).queryset().filter(order_status=2, is_delete=0)
        for obj in queryset:
            obj.count_down = int((obj.prepare_time - datetime.datetime.now()).days)
            if obj.count_down <= 0:
                obj.count_down = 0
                obj.order_status = 3
                obj.servicesdetail_set.all().update(order_status=2)
            obj.save()
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 待执行任务
class SSIProcessAdmin(object):
    list_display = ['name', 'count_down', 'mistake_tag', 'process_tag', 'order_category', 'order_type', 'prepare_time',
                    'services_info', 'quantity', 'received_num', 'completed_num', 'unhandle_num',
                    'memorandum', 'creator', 'create_time']

    actions = [RejectSelectedAction]

    list_filter = ['name', 'mistake_tag', 'process_tag', 'count_down', 'order_category', 'memorandum',
                   'creator', 'create_time']
    readonly_fields = ['id', 'name', 'count_down', 'mistake_tag', 'process_tag', 'order_category', 'prepare_time',
                       'services_info', 'quantity', 'creator', 'create_time', 'is_delete', 'order_type',
                       'received_num', 'completed_num', ]

    form_layout = [
        Fieldset('基本信息',
                 'name', 'order_category', 'order_type',),
        Fieldset('任务详情',
                 'prepare_time', 'services_info', ),
        Fieldset(None,
                 'process_tag', 'mistake_tag', 'order_status', 'finish_time', 'start_time', 'update_time', 'quantity',
                 'count_down', 'creator', 'is_delete', **{"style": "display:None"}),
    ]

    ordering = ['count_down']

    def queryset(self):
        queryset = super(SSIProcessAdmin, self).queryset().filter(order_status=3, is_delete=0)
        for obj in queryset:
            obj.count_down = int((obj.prepare_time - datetime.datetime.now()).days)
            obj.completed_num = obj.servicesdetail_set.all().filter(order_status=5).count()
            obj.received_num = obj.servicesdetail_set.all().filter(order_status=4).count()
            if obj.completed_num == obj.quantity:
                obj.order_status = 4
            obj.save()
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 待确认完成任务
class SSIFinishedAdmin(object):

    list_display = ['name', 'count_down', 'mistake_tag', 'process_tag', 'order_category', 'order_type', 'prepare_time',
                    'services_info', 'quantity', 'received_num', 'completed_num', 'memorandum', 'creator', 'create_time']

    actions = [FinishSSIAction]

    list_filter = ['name', 'mistake_tag', 'process_tag', 'count_down', 'order_category', 'memorandum',
                   'creator', 'create_time']
    readonly_fields = ['id', 'name', 'count_down', 'mistake_tag', 'process_tag', 'order_category', 'prepare_time',
                       'services_info', 'quantity', 'creator', 'create_time', 'is_delete', 'order_type',
                       'received_num', 'completed_num', ]
    form_layout = [
        Fieldset('基本信息',
                 'name', 'order_category', 'order_type',),
        Fieldset('任务详情',
                 'prepare_time', 'services_info', ),
        Fieldset(None,
                 'process_tag', 'mistake_tag', 'order_status', 'finish_time', 'start_time', 'update_time', 'quantity',
                 'count_down', 'creator', 'is_delete', **{"style": "display:None"}),
    ]

    def queryset(self):
        queryset = super(SSIFinishedAdmin, self).queryset().filter(order_status=4, is_delete=0)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 任务查询
class ServicesInfoAdmin(object):

    list_display = ['name', 'count_down', 'mistake_tag', 'process_tag', 'order_category', 'order_type', 'prepare_time',
                    'services_info', 'quantity', 'received_num', 'completed_num', 'memorandum', 'creator', 'create_time']

    actions = [SubmitSSIAction]

    list_filter = ['name', 'mistake_tag', 'process_tag', 'count_down', 'order_category', 'memorandum',
                   'creator', 'create_time']
    readonly_fields = ['id', 'name', 'count_down', 'mistake_tag', 'process_tag', 'order_category', 'prepare_time',
                       'services_info', 'quantity', 'memorandum', 'creator', 'create_time', 'is_delete', 'order_type',]
    form_layout = [
        Fieldset('基本信息',
                 'name', 'order_category', 'order_type',),
        Fieldset('任务详情',
                 'prepare_time', 'services_info', ),
        Fieldset(None,
                 'process_tag', 'mistake_tag', 'order_status', 'finish_time', 'start_time', 'update_time', 'quantity',
                 'count_down', 'creator', 'is_delete', **{"style": "display:None"}),
    ]

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 待生成任务明细
class SDCreateAdmin(object):
    list_display = ['target', 'services', 'mistake_tag', 'process_tag', 'warranty_sn', 'outcome',
                    'services_info', 'memorandum', 'order_type', 'order_status',
                    'creator', 'create_time']

    actions = []
    list_exclude = ['customer', 'ori_amount', ]
    list_filter = ['target', 'mistake_tag', 'process_tag', 'services__name', 'handler', 'memorandum', 'creator',
                   'create_time']
    readonly_fields = ['target', 'customer', 'services', 'services_info', 'order_type', 'outcome', 'memorandum']

    form_layout = [
        Fieldset('基本信息',
                 'services', 'order_type', 'target', 'services_info', 'warranty_sn',),
        Fieldset('执行结果',
                 'outcome', 'memorandum',),
        Fieldset(None,
                 'process_tag', 'mistake_tag', 'order_status', 'is_completed', 'handler', 'update_time', 'customer',
                 'handler', 'handle_time', '', 'creator', 'is_delete', **{"style": "display:None"}),
    ]
    ALLOWED_EXTENSIONS = ['xls', 'xlsx']

    INIT_FIELDS_DIC = {

        '关系任务': 'services',
        '延保码': 'warranty_sn',
        '任务对象': 'target',
    }

    import_data = True

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file', None)
        if file:
            result = self.handle_upload_file(request, file)
            self.message_user('结果提示：%s' % result)
        return super(SDCreateAdmin, self).post(request, *args, **kwargs)

    def handle_upload_file(self, request, _file):
        report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error": []}
        if '.' in _file.name and _file.name.rsplit('.')[-1] in self.__class__.ALLOWED_EXTENSIONS:
            df = pd.read_excel(_file, sheet_name=0, dtype=str)

            FILTER_FIELDS = ['延保码', '任务对象', '关系任务']

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
            _ret_verify_field = SDCreate.verify_mandatory(columns_key)
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
                _ret_verify_field = SDCreate.verify_mandatory(columns_key)
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
            report_dic["error"].append('只支持excel文件格式！')
            return report_dic

    @staticmethod
    def save_resources(request, resource):
        # 设置初始报告
        report_dic = {"successful": 0, "discard": 0, "false": 0, "repeated": 0, "error": []}
        batch_name = resource[0]['services']
        _q_service_order = ServicesInfo.objects.filter(name=batch_name)
        if _q_service_order.exists():
            service_order = _q_service_order[0]
        else:
            report_dic['error'].append('导入的任务名称不存在，核实后重试')
            return report_dic
        for row in resource:
            _q_warranty = SDCreate.objects.filter(target=row['target'], services=service_order)
            if _q_warranty.exists():
                warranty = _q_warranty[0]
                warranty.warranty_sn = row['warranty_sn']
                warranty.save()
                report_dic['successful'] += 1
            else:
                report_dic['error'].append('导入的对象：%s 不存在任务' % row['target'])
                report_dic["false"] += 1
                continue
        return report_dic

    def queryset(self):
        queryset = super(SDCreateAdmin, self).queryset().filter(order_status=1, is_delete=0)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 待领取任务明细
class SDDistributeAdmin(object):
    list_display = ['target', 'services', 'mistake_tag', 'process_tag', 'warranty_sn', 'outcome',
                    'services_info', 'memorandum', 'order_type', 'order_status',
                    'creator', 'create_time']

    actions = [GetSDAction, FilterSDAction]
    list_exclude = ['customer', 'ori_amount', ]
    list_filter = ['target', 'mistake_tag', 'process_tag', 'services__name', 'handler', 'memorandum', 'creator',
                   'create_time']
    readonly_fields = ['target', 'customer', 'services', 'services_info', 'order_type',]

    form_layout = [
        Fieldset('基本信息',
                 'services', 'order_type', 'target', 'services_info',),
        Fieldset('执行结果',
                 'outcome', 'memorandum', ),
        Fieldset(None,
                 'process_tag', 'mistake_tag', 'order_status', 'is_completed', 'handler', 'update_time', 'customer',
                 'handle_time', 'creator', 'is_delete', **{"style": "display:None"}),
    ]

    def queryset(self):
        queryset = super(SDDistributeAdmin, self).queryset().filter(order_status=2, is_delete=0)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 待执行任务明细
class SDProcessAdmin(object):
    list_display = ['target', 'services', 'mistake_tag', 'process_tag', 'warranty_sn', 'outcome',
                    'services_info', 'memorandum', 'order_type', 'order_status',
                    'creator', 'create_time']

    actions = [FinishWWAction, FinishMSAction, ConfirmSDAction, RejectSelectedAction]
    list_exclude = ['customer', 'ori_amount', ]
    list_filter = ['target', 'outcome', 'mistake_tag', 'process_tag', 'services__name', 'handler', 'memorandum', 'creator',
                   'create_time']
    readonly_fields = ['target', 'customer', 'services', 'services_info', 'order_type']
    search_fields = ['target']
    form_layout = [
        Fieldset('基本信息',
                 'services', 'order_type', 'target', 'services_info', ),
        Fieldset('执行结果',
                 'outcome', 'memorandum', ),
        Fieldset(None,
                 'process_tag', 'mistake_tag', 'order_status', 'is_completed', 'handler', 'customer',
                 'warranty_sn', 'handle_time', 'creator', 'is_delete', **{"style": "display:None"}),
    ]

    def save_models(self):
        obj = self.new_obj
        obj.handle_time = datetime.datetime.now()
        obj.handler = self.request.user.username
        obj.save()
        super().save_models()

    def queryset(self):
        queryset = super(SDProcessAdmin, self).queryset()
        queryset = queryset.filter(order_status=3, handler=self.request.user.username, is_delete=0)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 待反馈任务明细
class SDFeedbackAdmin(object):
    list_display = ['target', 'services', 'mistake_tag', 'process_tag', 'warranty_sn', 'outcome',
                    'services_info', 'memorandum', 'order_type', 'order_status', 'handler', 'handle_time',
                    'creator', 'create_time']

    actions = [CreateRepeatAction, FilterSDAction]
    list_exclude = ['customer', 'ori_amount', ]
    list_filter = ['target', 'services__name', 'mistake_tag', 'process_tag', 'handler', 'handle_time', 'order_type',
                   'memorandum', 'creator', 'create_time']
    readonly_fields = ['target', 'customer', 'services', 'services_info', 'order_type']

    form_layout = [
        Fieldset('基本信息',
                 'services', 'order_type', 'target', 'services_info', ),
        Fieldset('执行结果',
                 'outcome', 'memorandum', ),
        Fieldset(None,
                 'process_tag', 'mistake_tag', 'order_status', 'is_completed', 'handler', 'update_time', 'customer',
                 'handle_time', 'creator', 'is_delete', **{"style": "display:None"}),
    ]

    def queryset(self):
        queryset = super(SDFeedbackAdmin, self).queryset()
        queryset = queryset.filter(order_status=4, is_delete=0)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


# 任务明细查询
class ServicesDetailAdmin(object):
    list_display = ['target', 'services', 'mistake_tag', 'process_tag', 'warranty_sn', 'outcome',
                    'services_info', 'memorandum', 'order_type', 'order_status', 'handle_time', 'handler',
                    'creator', 'create_time']

    actions = []
    list_exclude = ['customer', 'ori_amount', ]
    list_filter = ['target', 'order_type', 'order_status', 'mistake_tag', 'process_tag', 'handle_time',
                   'services__name', 'handler', 'memorandum', 'creator', 'create_time']
    readonly_fields = ['handle_time', 'target', 'customer', 'services', 'services_info', 'order_type']

    form_layout = [
        Fieldset('基本信息',
                 'services', 'order_type', 'target', 'services_info', ),
        Fieldset('执行结果',
                 'outcome', 'memorandum', ),
        Fieldset(None,
                 'process_tag', 'mistake_tag', 'order_status', 'is_completed', 'handler', 'update_time', 'customer',
                 'handle_time', 'creator', 'is_delete', **{"style": "display:None"}),
    ]
    def has_add_permission(self):
        # 禁用添加按钮
        return False


xadmin.site.register(SSICreate, SSICreateAdmin)
xadmin.site.register(SSIDistribute, SSIDistributeAdmin)
xadmin.site.register(SSIProcess, SSIProcessAdmin)
xadmin.site.register(SSIFinished, SSIFinishedAdmin)

xadmin.site.register(ServicesInfo, ServicesInfoAdmin)

xadmin.site.register(SDCreate, SDCreateAdmin)
xadmin.site.register(SDDistribute, SDDistributeAdmin)
xadmin.site.register(SDProcess, SDProcessAdmin)
xadmin.site.register(SDFeedback, SDFeedbackAdmin)
xadmin.site.register(ServicesDetail, ServicesDetailAdmin)






