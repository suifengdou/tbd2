# -*- coding: utf-8 -*-
# @Time    : 2020/4/14 14:40
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

from .models import DepartmentInfo


class DepartmentInfoAdmin(object):
    list_display = ['name', 'd_id']
    search_fields = ['name', 'd_id']

    def save_models(self):
        obj = self.new_obj
        obj.creator = self.request.user.username
        obj.save()
        super().save_models()


xadmin.site.register(DepartmentInfo, DepartmentInfoAdmin)