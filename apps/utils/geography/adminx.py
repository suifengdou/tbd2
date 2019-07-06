# -*- coding: utf-8 -*-
# @Time    : 2019/6/6 9:36
# @Author  : Hann
# @Site    : 
# @File    : adminx.py
# @Software: PyCharm


import xadmin

from .models import NationalityInfo, ProvinceInfo, CityInfo


class NationalityAdmin(object):
    pass


class ProvinceAdmin(object):

    def queryset(self):
        request = self.request
        qs = super(ProvinceAdmin, self).queryset()
        return qs


class CityAdmin(object):

    def queryset(self):
        request = self.request
        qs = super(CityAdmin, self).queryset()
        return qs


xadmin.site.register(NationalityInfo, NationalityAdmin)
xadmin.site.register(ProvinceInfo, ProvinceAdmin)
xadmin.site.register(CityInfo, CityAdmin)