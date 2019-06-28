# -*- coding: utf-8 -*-
# @Time    : 2019/4/9 20:58
# @Author  : Hann
# @Site    :
# @File    : models.py
# @Software: PyCharm


from django.db import models


from db.base_model import BaseModel
from apps.utils.geography.models import NationalityInfo


# Create your models here.
class GoodsInfo(BaseModel):
    GOODS_TYPE = (
        ("VAC", "吸尘器"),
        ("DMC", "除螨仪"),
        ("VAR", "智能机器人"),
        ("OTH", "其他"),
    )

    GOODS_ATTRIBUTE = (
        (0, "整机"),
        (1, "配件"),
        (2, "礼品"),
    )

    goods_id = models.CharField(unique=True, max_length=30, verbose_name='货品编码', db_index=True)
    goods_name = models.CharField(unique=True, max_length=60, verbose_name='货品名称', db_index=True)
    category = models.CharField(choices=GOODS_TYPE, default="OTH", max_length=10, verbose_name='货品类别')
    goods_attribute = models.IntegerField(choices=GOODS_ATTRIBUTE, default=0, verbose_name='货品属性')
    goods_number = models.CharField(unique=True, max_length=10, verbose_name='机器排序')
    size = models.CharField(null=True, blank=True, max_length=50, verbose_name='规格')
    width = models.IntegerField(null=True, blank=True, verbose_name='长')
    height = models.IntegerField(null=True, blank=True, verbose_name='宽')
    depth = models.IntegerField(null=True, blank=True, verbose_name='高')
    weight = models.IntegerField(null=True, blank=True, verbose_name='重量')

    class Meta:
        verbose_name = '货品信息表'
        verbose_name_plural = verbose_name
        db_table = 'oms_m_goodsinfo'

    def __str__(self):
        return self.goods_name


class PartInfo(GoodsInfo):
    class Meta:
        verbose_name = '配件信息表'
        verbose_name_plural = verbose_name
        proxy = True

    def __str__(self):
        return self.goods_name


class MachineInfo(GoodsInfo):
    class Meta:
        verbose_name = '机器信息表'
        verbose_name_plural = verbose_name
        proxy = True

    def __str__(self):
        return self.goods_name

















