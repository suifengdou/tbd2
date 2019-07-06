# -*- coding: utf-8 -*-
# @Time    : 2019/4/9 20:58
# @Author  : Hann
# @Site    :
# @File    : xadmin.py.py
# @Software: PyCharm

import xadmin

from .models import GoodsInfo, PartInfo, MachineInfo


class GoodsInfoAdmin(object):
    list_display = ['goods_name', 'goods_id', 'goods_attribute', 'goods_number']
    search_fields = ['goods_name']
    relfield_style = 'fk-ajax'


class MachineInfoAdmin(object):
    list_display = ['goods_name', 'goods_id', 'goods_attribute', 'goods_number']
    search_fields = ['goods_id', 'goods_name']
    # 设置这个外键用搜索的方式输入
    relfield_style = 'fk-ajax'

    def queryset(self):
        qs = super(MachineInfoAdmin, self).queryset()
        qs = qs.filter(goods_attribute=0)
        return qs


class PartInfoAdmin(object):
    list_display = ['goods_name']
    search_fields = ['goods_name']
    relfield_style = 'fk-ajax'

    def queryset(self):
        qs = super(PartInfoAdmin, self).queryset()
        qs = qs.filter(goods_attribute=1)
        return qs


xadmin.site.register(MachineInfo, MachineInfoAdmin)
xadmin.site.register(PartInfo, PartInfoAdmin)
xadmin.site.register(GoodsInfo, GoodsInfoAdmin)

