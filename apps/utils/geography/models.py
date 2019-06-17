# -*- coding: utf-8 -*-
# @Time    : 2019/5/31 15:52
# @Author  : Hann
# @Site    : 
# @File    : geography.py
# @Software: PyCharm

from django.db import models
import django.utils.timezone as timezone

from db.base_model import BaseModel


class NationalityInfo(BaseModel):
    nationality = models.CharField(unique=True, max_length=100, verbose_name='国家及地区')
    abbreviation = models.CharField(unique=True, max_length=3, verbose_name='缩写')
    area_code = models.CharField(unique=True, max_length=10, verbose_name='电话区号')

    class Meta:
        verbose_name = '国家及地区'
        verbose_name_plural = verbose_name
        db_table = 'util_geo_nationality'

    def __str__(self):
        return self.nationality


class ProvinceInfo(BaseModel):
    nationality = models.ForeignKey(NationalityInfo, models.CASCADE, verbose_name='国家')
    province = models.CharField(unique=True, max_length=150, verbose_name="省份")
    area_code = models.CharField(unique=True, max_length=10, verbose_name='电话区号')

    class Meta:
        verbose_name = '省份'
        verbose_name_plural = verbose_name
        db_table = 'util_geo_province'

    def __str__(self):
        return self.province


class CityInfo(BaseModel):
    nationality = models.ForeignKey(NationalityInfo, on_delete=models.CASCADE, verbose_name='国家')
    province = models.ForeignKey(ProvinceInfo, on_delete=models.CASCADE, verbose_name='省份')
    city = models.CharField(unique=True, max_length=100, verbose_name='城市')
    area_code = models.CharField(max_length=10, verbose_name='电话区号')

    class Meta:
        verbose_name = '城市'
        verbose_name_plural = verbose_name
        db_table = 'util_geo_city'

    def __str__(self):
        return self.city


