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

from django.contrib.admin.utils import get_deleted_objects

from django.core.files.uploadedfile import InMemoryUploadedFile

import xadmin
from xadmin.plugins.actions import BaseActionView
from xadmin.views.base import filter_hook
from xadmin.util import model_ngettext
from xadmin.layout import Fieldset, Main, Row, Side

from .models import SSICreate, SSIDistribute, SSIOnProcess, SSIProcess, ServicesInfo, SDDistribute, SDProcess, ServicesDetail
from .models import SIMirror, SDMirror

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


class SSICreateAdmin(object):
    list_display = ['name', 'mistake_tag', 'process_tag', 'order_category', 'prepare_time', 'services_info',
                    'quantity', 'memorandum', 'creator', 'create_time']

    actions = []

    list_filter = ['name', 'mistake_tag', 'process_tag', 'order_category', 'memorandum', 'creator', 'create_time']

    form_layout = [
        Fieldset('基本信息',
                 Row('name', 'order_category', ),
                 'memorandum',
                 Row('creator', 'create_time', ), ),
        Fieldset(None,
                 'update_time', 'is_delete', **{"style": "display:None"}),
    ]


class SSIDistributeAdmin(object):
    pass


class SSIOnProcessAdmin(object):
    pass


class SSIProcessAdmin(object):
    pass



class ServicesInfoAdmin(object):
    pass



class SDDistributeAdmin(object):
    pass



class SDProcessAdmin(object):
    pass


class ServicesDetailAdmin(object):
    pass


class SIMirrorAdmin(object):
    pass


class SDMirrorAdmin(object):
    pass


xadmin.site.register(SSICreate, SSICreateAdmin)
xadmin.site.register(SSIDistribute, SSIDistributeAdmin)
xadmin.site.register(SSIOnProcess, SSIOnProcessAdmin)
xadmin.site.register(SSIProcess, SSIProcessAdmin)
xadmin.site.register(ServicesInfo, ServicesInfoAdmin)
xadmin.site.register(SDDistribute, SDDistributeAdmin)
xadmin.site.register(SDProcess, SDProcessAdmin)
xadmin.site.register(ServicesDetail, ServicesDetailAdmin)
xadmin.site.register(SIMirror, SIMirrorAdmin)
xadmin.site.register(SDMirror, SDMirrorAdmin)





