# -*- coding: utf-8 -*-
# @Time    : 2020/4/24 16:07
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
from xadmin.layout import Fieldset

from .models import DialogTag, DialogTB, DetailTB

ACTION_CHECKBOX_NAME = '_selected_action'


class DialogTagAdmin(object):
    list_display = []


class DialogTBAdmin(object):
    list_display = []


class DetailTBAdmin(object):
    list_display = []


xadmin.site.register(DialogTag, DialogTagAdmin)
xadmin.site.register(DialogTB, DialogTBAdmin)
xadmin.site.register(DetailTB, DetailTBAdmin)