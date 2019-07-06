
# -*- coding: utf-8 -*-
# @Time    : 2019/4/9 21:42
# @Author  : Hann
# @Site    : 
# @File    : adminx.py.py
# @Software: PyCharm

import xadmin

from .models import SFConsignation


class SFConsignationAdmin(object):
    list_display = ["application_time", "consignor", "information", "remark",
                   "feedback_time", "express_id", "is_operate", "handlingstatus", "create_time", "id", "creator"]
    search_fields = ["express_id"]
    list_filter = ["consignor", "handlingstatus"]


xadmin.site.register(SFConsignation, SFConsignationAdmin)