# -*- coding: utf-8 -*-
# @Time    : 2019/6/24 10:15
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

from .models import WarehouseTypeInfo, WarehouseInfo

class WarehouseTypeInfoAdmin(object):
    pass


class WarehouseInfoAdmin(object):
    pass


xadmin.site.register(WarehouseTypeInfo, WarehouseTypeInfoAdmin)
xadmin.site.register(WarehouseInfo, WarehouseInfoAdmin)