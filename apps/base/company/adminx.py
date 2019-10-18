# -*- coding: utf-8 -*-
# @Time    : 2019/7/5 8:59
# @Author  : Hann
# @Site    : 
# @File    : adminx.py
# @Software: PyCharm
import math
import datetime
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.db import router
from django.utils.encoding import force_text
from django.template.response import TemplateResponse
from django.contrib.admin.utils import get_deleted_objects

import xadmin
from xadmin.plugins.actions import BaseActionView
from xadmin.views.base import filter_hook
from xadmin.util import model_ngettext
from xadmin.layout import Fieldset


from .models import CompanyInfo, LogisticsInfo, ManuInfo, WareInfo

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
    def delete_models(self, queryset):
        n = queryset.count()
        if n:
            for obj in queryset:
                if obj.order_status == 1:
                    obj.order_status -= 1
                    obj.save()
                    if obj.order_status == 0:
                        self.message_user("%s 取消成功" % obj.express_id, "success")
                    else:
                        self.message_user("%s 驳回上一级成功" % obj.express_id, "success")
                else:
                    n -= 1
                    self.message_user("%s 公司状态错误，请检查，取消出错。" % obj.express_id, "error")
            self.message_user("成功驳回 %(count)d %(items)s." % {"count": n, "items": model_ngettext(self.opts, n)},
                              'success')
        return None

    @filter_hook
    def do_action(self, queryset):
        # Check that the user has delete permission for the actual model
        if not self.has_delete_permission():
            raise PermissionDenied

        using = router.db_for_write(self.model)

        # Populate deletable_objects, a data structure of all related objects that
        # will also be deleted.
        deletable_objects, model_count, perms_needed, protected = get_deleted_objects(
            queryset, self.opts, self.user, self.admin_site, using)

        # The user has already confirmed the deletion.
        # Do the deletion and return a None to display the change list view again.
        if self.request.POST.get('post'):
            if perms_needed:
                raise PermissionDenied
            self.delete_models(queryset)
            # Return None to display the change list page again.
            return None

        if len(queryset) == 1:
            objects_name = force_text(self.opts.verbose_name)
        else:
            objects_name = force_text(self.opts.verbose_name_plural)

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


class CompanyInfoAdmin(object):
    list_display = ['company_name', 'tax_fil_number', 'status', 'category']
    list_filter = ['category']
    actions = [RejectSelectedAction, ]

    def save_models(self):
        obj = self.new_obj
        request = self.request
        obj.creator = request.user.username
        obj.save()
        super().save_models()


class LogisticsInfoAdmin(object):
    list_display = ['company_name', 'tax_fil_number', 'status', 'category']
    relfield_style = 'fk-ajax'

    def queryset(self):
        queryset = super(LogisticsInfoAdmin, self).queryset()
        queryset = queryset.filter(category=1)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


class WareInfoAdmin(object):
    list_display = ['company_name', 'tax_fil_number', 'status', 'category']
    relfield_style = 'fk-ajax'

    def queryset(self):
        queryset = super(WareInfoAdmin, self).queryset()
        queryset = queryset.filter(category=2)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


class ManuInfoAdmin(object):
    list_display = ['company_name', 'tax_fil_number', 'status', 'category']
    relfield_style = 'fk-ajax'

    def queryset(self):
        queryset = super(ManuInfoAdmin, self).queryset()
        queryset = queryset.filter(category=3)
        return queryset

    def has_add_permission(self):
        # 禁用添加按钮
        return False


xadmin.site.register(LogisticsInfo, LogisticsInfoAdmin)
xadmin.site.register(WareInfo, WareInfoAdmin)
xadmin.site.register(ManuInfo, ManuInfoAdmin)
xadmin.site.register(CompanyInfo, CompanyInfoAdmin)