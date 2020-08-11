# -*- coding: utf-8 -*-
# @Time    : 2019/5/13 10:41
# @Author  : Hann
# @Site    : 
# @File    : adminx.py
# @Software: PyCharm


import xadmin
from xadmin import views
from django.contrib.auth import get_user_model


class GlobalSettings(object):
    site_title = 'UltraTool'
    site_footer = 'UltraTool V0.5.0.40'
    menu_style = 'accordion'


xadmin.site.register(views.CommAdminView, GlobalSettings)


