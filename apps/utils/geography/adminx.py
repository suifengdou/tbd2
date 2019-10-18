# -*- coding: utf-8 -*-
# @Time    : 2019/6/6 9:36
# @Author  : Hann
# @Site    : 
# @File    : adminx.py
# @Software: PyCharm


import xadmin

from .models import NationalityInfo, ProvinceInfo, CityInfo, DistrictInfo


class NationalityAdmin(object):
    list_display = ['nationality', 'abbreviation', 'area_code']
    pass


class ProvinceAdmin(object):
    list_display = ['nationality', 'province', 'area_code']

    def queryset(self):
        request = self.request
        qs = super(ProvinceAdmin, self).queryset()
        return qs


class CityAdmin(object):
    list_display = ['nationality', 'province', 'city', 'area_code']

    def queryset(self):
        request = self.request
        qs = super(CityAdmin, self).queryset()
        return qs

class DistrictInfoAdmin(object):
    list_display = ['nationality', 'province', 'city', 'district']


xadmin.site.register(NationalityInfo, NationalityAdmin)
xadmin.site.register(ProvinceInfo, ProvinceAdmin)
xadmin.site.register(CityInfo, CityAdmin)
xadmin.site.register(DistrictInfo, DistrictInfoAdmin)