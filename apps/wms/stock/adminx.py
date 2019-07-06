# -*- coding: utf-8 -*-
# @Time    : 2019/6/24 20:12
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

from .models import StockInfo, StockMachineInfo, StockPartInfo, StockGiftInfo


class StockInfoAdmin(object):
    list_display = ["goods_name", "goods_id", "category", "size", "warehouse", "quantity", "occupied_quantity", "available_quantity"]


class StockMachineInfoAdmin(object):
    list_display = ["goods_name", "goods_id", "category", "size", "warehouse", "quantity", "occupied_quantity",
                    "available_quantity"]
    list_filter = ["warehouse"]
    search_fields = ["goods_name", "goods_id"]

    def queryset(self):
        queryset = super(StockMachineInfoAdmin, self).queryset()
        queryset = queryset.filter(category=0)
        return queryset


class StockPartInfoAdmin(object):
    list_display = ["goods_name", "goods_id", "category", "size", "warehouse", "quantity", "occupied_quantity",
                    "available_quantity"]
    list_filter = ["warehouse"]
    search_fields = ["goods_name", "goods_id"]

    def queryset(self):
        queryset = super(StockPartInfoAdmin, self).queryset()
        queryset = queryset.filter(category=1)
        return queryset


class StockGiftInfoAdmin(object):
    list_display = ["goods_name", "goods_id", "category", "size", "warehouse", "quantity", "occupied_quantity",
                    "available_quantity"]
    list_filter = ["warehouse"]
    search_fields = ["goods_name", "goods_id"]

    def queryset(self):
        queryset = super(StockGiftInfoAdmin, self).queryset()
        queryset = queryset.filter(category=2)
        return queryset


xadmin.site.register(StockMachineInfo, StockMachineInfoAdmin)
xadmin.site.register(StockPartInfo, StockPartInfoAdmin)
xadmin.site.register(StockGiftInfo, StockGiftInfoAdmin)
xadmin.site.register(StockInfo, StockInfoAdmin)


