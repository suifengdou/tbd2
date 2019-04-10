# -*- coding: utf-8 -*-
# @Time    : 2019/4/9 20:58
# @Author  : Hann
# @Site    : 
# @File    : xadmin.py.py
# @Software: PyCharm

import xadmin

from .models import MaintenanceInfo, MaintenanceHandlingInfo, MaintenanceSummary


class MaintenanceInfoAdmin(object):
     list_display = ['maintenance_order_id', 'warehouse', 'completer', 'maintenance_type', 'fault_type', 'machine_sn', 'appraisal', 'shop', 'finish_time', 'buyer_nick', 'sender_mobile', 'goods_name', 'is_guarantee']
     search_fields = ['maintenance_order_id', 'sender_mobile']
     list_filter = ['warehouse', 'fault_type', 'appraisal', 'finish_time']


class MaintenanceHandlingInfoAdmin(object):
    list_display = ['maintenance_order_id', 'warehouse', 'maintenance_type', 'fault_type', 'machine_sn', 'appraisal',
                    'shop', 'finish_time', 'buyer_nick', 'sender_name', 'sender_mobile', 'sender_area', 'goods_name',
                    'is_guarantee', 'province', 'city', 'district', 'handling_status', 'repeat_tag', 'goods_type']
    search_fields = ['maintenance_order_id', 'sender_mobile']
    list_filter = ['shop', 'goods_type', 'finish_time']


class MaintenanceSummaryAdmin(object):
    pass


xadmin.site.register(MaintenanceInfo, MaintenanceInfoAdmin)
xadmin.site.register(MaintenanceHandlingInfo, MaintenanceHandlingInfoAdmin)
xadmin.site.register(MaintenanceSummary, MaintenanceSummaryAdmin)