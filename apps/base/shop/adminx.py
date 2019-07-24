# -*- coding: utf-8 -*-
# @Time    : 2019/7/5 8:59
# @Author  : Hann
# @Site    : 
# @File    : adminx.py.py
# @Software: PyCharm

import xadmin


from .models import ShopInfo, PlatformInfo


class ShopInfoAdmin(object):
    pass


class PlatformInfoAdmin(object):
    pass


xadmin.site.register(ShopInfo, ShopInfoAdmin)
xadmin.site.register(PlatformInfo, PlatformInfoAdmin)