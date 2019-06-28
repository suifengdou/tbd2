# -*- coding: utf-8 -*-
# @Time    : 2019/6/24 10:13
# @Author  : Hann
# @Site    : 
# @File    : adminx.py
# @Software: PyCharm

from django.core.exceptions import PermissionDenied
import pandas as pd
import xadmin
from xadmin.plugins.actions import BaseActionView
from xadmin.views.base import filter_hook
from xadmin.util import model_ngettext


from .models import ManufactoryInfo

class ManufactoryInfoAdmin(object):
    pass


xadmin.site.register(ManufactoryInfo, ManufactoryInfoAdmin)