# -*- coding: utf-8 -*-
# @Time    : 2019/5/13 10:41
# @Author  : Hann
# @Site    : 
# @File    : adminx.py
# @Software: PyCharm


import xadmin
from xadmin import views

class GlobalSettings(object):
    site_title = 'TBD2后台管理系统'
    site_footer = 'TBD2'
    menu_style = 'accordion'


xadmin.site.register(views.CommAdminView, GlobalSettings)