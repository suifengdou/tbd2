# -*- coding: utf-8 -*-
# @Time    : 2019/7/5 8:59
# @Author  : Hann
# @Site    : 
# @File    : adminx.py
# @Software: PyCharm

import xadmin


from .models import CompanyInfo


class CompanyInfoAdmin(object):
    pass


xadmin.site.register(CompanyInfo, CompanyInfoAdmin)