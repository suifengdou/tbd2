# -*- coding: utf-8 -*-
# @Time    : 2019/7/5 8:59
# @Author  : Hann
# @Site    : 
# @File    : adminx.py.py
# @Software: PyCharm

import xadmin


from .models import ShopInfo, PlatformInfo


class ShopInfoAdmin(object):
    list_display = ['shop_name', 'shop_id', 'platform', 'group_name', 'company', 'status']
    # relfield_style = 'fk-ajax'


class PlatformInfoAdmin(object):
    list_display = ['platform', 'category', 'status']
    list_editable = ['category']


xadmin.site.register(ShopInfo, ShopInfoAdmin)
xadmin.site.register(PlatformInfo, PlatformInfoAdmin)