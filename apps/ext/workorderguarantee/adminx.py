# -*- coding: utf-8 -*-
# @Time    : 2020/6/8 10:39
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

from django.contrib.admin.utils import get_deleted_objects

import pandas as pd
import xadmin
from xadmin.plugins.actions import BaseActionView
from xadmin.views.base import filter_hook
from xadmin.util import model_ngettext
from xadmin.layout import Fieldset, Main, Row, Side

from .models import WorkOrder, WOCategory, WORCreate, WOPCreate, WORCheck, WOSCheck, WOFinish


ACTION_CHECKBOX_NAME = '_selected_action'


# 驳回审核
class RejectSelectedAction(BaseActionView):

    action_name = "reject_selected"
    description = '驳回选中的工单'

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
                if obj.order_status == 3:
                    obj.order_status -= 3
                    obj.save()
                    self.message_user("%s 取消成功" % obj.express_id, "success")
                elif obj.order_status in [1, 2, 4, 5, 6, 7]:
                    if obj.wo_category == 1 and obj.order_status == 4:
                        obj.order_status -= 2
                        obj.save()
                        self.message_user("%s 驳回上一级成功" % obj.express_id, "success")
                    else:
                        obj.order_status -= 1
                        obj.save()
                        if obj.order_status == 0:
                            self.message_user("%s 取消成功" % obj.express_id, "success")
                        else:
                            self.message_user("%s 驳回上一级成功" % obj.express_id, "success")
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


# 创建维修工单类型界面
class WOCategoryAdmin(object):
    list_display = ['order_status', 'name']
    list_filter = []
    search_fields = []




# 逆向创建维修工单界面
class WORCreateAdmin(object):
    list_display = ['order_status', 'category', 'express_id', 'goods_name', 'information', 'creator',
                    'memo', 'process_tag', 'mistake_tag', 'wo_category', ]

    form_layout = [
            Fieldset('关键信息',
                     Row('express_id', 'goods_name'),
                     Row('category',),),
            Fieldset('必填内容',
                     'information'),
            Fieldset(None,
                     'mistake_tag', 'submit_time', 'servicer', 'servicer_feedback', 'handler', 'services_interval',
                     'handle_time', 'process_interval', 'feedback', 'memo', 'order_status',
                     'creator', 'wo_category', 'process_tag', **{"style": "display:None"})]


# 正向创建维修工单界面
class WOPCreateAdmin(object):
    list_display = []


# 客服审核维修工单界面
class WOSCheckAdmin(object):
    list_display = []


# 技术审核维修工单界面
class WORCheckAdmin(object):
    list_display = []


# 维修工单终审界面
class WOFinishAdmin(object):
    list_display = []


# 维修工单查询
class WorkOrderAdmin(object):
    list_display = []


xadmin.site.register(WOCategory, WOCategoryAdmin)
xadmin.site.register(WORCreate, WORCreateAdmin)
xadmin.site.register(WOPCreate, WOPCreateAdmin)
xadmin.site.register(WORCheck, WORCheckAdmin)
xadmin.site.register(WOSCheck, WOSCheckAdmin)
xadmin.site.register(WOFinish, WOFinishAdmin)
xadmin.site.register(WorkOrder, WorkOrderAdmin)

