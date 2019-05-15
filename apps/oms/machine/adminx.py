# -*- coding: utf-8 -*-
# @Time    : 2019/4/9 20:58
# @Author  : Hann
# @Site    : 
# @File    : xadmin.py.py
# @Software: PyCharm

import xadmin

from .models import MachineOrder, MachineSN, FaultMachineSN, GoodFaultSummary, FactoryFaultSummary, BatchFaultSummary, MachineInfo


class MachineOrderAdmin(object):
    list_display = ['identification', 'mfd', 'goods_id', 'manufactory', 'order_id', 'quantity', 'msn_segment']
    search_fields = ['manufactory', 'goods_id', 'order_id']
    list_filter = ['mfd', 'goods_id', 'manufactory']


class MachineSNAdmin(object):
    list_display = ['mfd', 'm_sn', 'batch_number', 'manufactory', 'goods_id']
    search_fields = ['mfd', 'm_sn', 'batch_number', 'manufactory', 'goods_id']
    list_filter = ['mfd', 'batch_number', 'manufactory', 'goods_id']


class FaultMachineSNAdmin(object):
    list_display = ['mfd', 'finish_time', 'm_sn', 'batch_number', 'manufactory', 'goods_id', 'appraisal']
    list_filter = ['mfd', 'finish_time', 'batch_number', 'manufactory', 'goods_id', 'appraisal']


class MachineInfoAdmin(object):
    list_display = ['machine_id', 'machine_name', 'machine_type', 'machine_number']
    search_fields = ['machine_id', 'machine_name']
    list_filter = ['machine_type']
    # 设置这个外键用搜索的方式输入
    relfield_style = 'fk-ajax'


xadmin.site.register(MachineOrder, MachineOrderAdmin)
xadmin.site.register(MachineSN, MachineSNAdmin)
xadmin.site.register(FaultMachineSN, FaultMachineSNAdmin)
xadmin.site.register(MachineInfo, MachineInfoAdmin)
