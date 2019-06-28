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

from .models import StockInfo, StockInOrderInfo, StockOutInfo


class StockInOrderInfoAdmin(object):
    list_display = ["source_order_id", "status", "category", "batch_num", "planorder_id", "warehouse", "goods_name", "goods_id", "quantity", "occupied_inventory", "available_inventory"]
    list_filter = ["category", "warehouse", "goods_name"]


class StockOutInfoAdmin(object):
    list_display = ["stockout_id", "source_order_id", "status", "category", "goods_name", "goods_id", "quantity",
                    "warehouse", "nickname", "receiver", "province", "city", "district", "mobile", "memorandum"]



class StockInfoAdmin(object):
    list_display = ["goods_name", "goods_id", "category", "size", "warehouse", "inventory", "occupied_inventory", "available_inventory"]


xadmin.site.register(StockInOrderInfo, StockInOrderInfoAdmin)
xadmin.site.register(StockOutInfo, StockOutInfoAdmin)
xadmin.site.register(StockInfo, StockInfoAdmin)