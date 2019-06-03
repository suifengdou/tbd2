# -*- coding: utf-8 -*-
# @Time    : 2019/5/31 15:52
# @Author  : Hann
# @Site    : 
# @File    : geography.py
# @Software: PyCharm

from django.db import models
import django.utils.timezone as timezone

from db.base_model import BaseModel
from tbd2.settings import AUTH_USER_MODEL


class NationalityInfo(BaseModel):
    nationality = models.CharField(max_length=100, verbose_name='国家')

    class Meta:
        verbose_name = '国家'
        verbose_name_plural = verbose_name
        db_table = 'util-geo-nationality'

    def __str__(self):
        return self.nationality


class ProvinceInfo(BaseModel):
    nationality = models.ForeignKey(NationalityInfo, models.CASCADE, verbose_name='国家')
    province = models.CharField(max_length=150, verbose_name="省份")

    class Meta:
        verbose_name = '省份'
        verbose_name_plural = verbose_name
        db_table = 'util-geo-province'

    def __str__(self):
        return self.province


class CityInfo(BaseModel):
    nationality = models.ForeignKey(NationalityInfo, on_delete=models.CASCADE, verbose_name='国家')
    province = models.ForeignKey(ProvinceInfo, on_delete=models.CASCADE, verbose_name='省份')
    city = models.CharField(max_length=100, verbose_name='城市')

    class Meta:
        verbose_name = '城市'
        verbose_name_plural = verbose_name
        db_table = 'util-geo-city'

    def __str__(self):
        return self.city


