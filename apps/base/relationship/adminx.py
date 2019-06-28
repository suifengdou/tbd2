# -*- coding: utf-8 -*-
# @Time    : 2019/6/24 11:22
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


from .models import GoodsToManufactoryInfo, PartToProductInfo, CusPartToManufactoryInfo, MachineToManufactoryInfo, PartToManufactoryInfo, ManufactoryToWarehouse


class MachineToManufactoryInfoAdmin(object):
    list_display = ["goods_name", "manufactory", "status", "category"]

    def queryset(self):
        queryset = super(MachineToManufactoryInfoAdmin, self).queryset()
        queryset = queryset.filter(category=0)
        return queryset


class CusPartToManufactoryInfoAdmin(object):
    list_display = ["goods_name", "manufactory", "status", "category"]

    def queryset(self):
        queryset = super(CusPartToManufactoryInfoAdmin, self).queryset()
        queryset = queryset.filter(category=1)
        return queryset


class PartToManufactoryInfoAdmin(object):
    list_display = ["goods_name", "manufactory", "status", "category"]

    def queryset(self):
        queryset = super(PartToManufactoryInfoAdmin, self).queryset()
        queryset = queryset.filter(category=3)
        return queryset


class GoodsToManufactoryInfoAdmin(object):
    list_display = ["goods_name", "manufactory", "status", "category"]


class PartToProductInfoAdmin(object):
    list_display = ["machine_name", "part_name", "magnification", "status"]



class ManufactoryToWarehouseAdmin(object):
    list_display = ["manufactory", "warehouse", "status"]



xadmin.site.register(MachineToManufactoryInfo, MachineToManufactoryInfoAdmin)
xadmin.site.register(CusPartToManufactoryInfo, CusPartToManufactoryInfoAdmin)
xadmin.site.register(PartToManufactoryInfo, PartToManufactoryInfoAdmin)
xadmin.site.register(GoodsToManufactoryInfo, GoodsToManufactoryInfoAdmin)
xadmin.site.register(PartToProductInfo, PartToProductInfoAdmin)
xadmin.site.register(ManufactoryToWarehouse, ManufactoryToWarehouseAdmin)