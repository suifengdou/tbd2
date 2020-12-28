from django.db import models

# Create your models here.
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
    ATTRIBUTE = (
        ("VAC", "吸尘器"),
        ("DMC", "除螨仪"),
        ("VAR", "智能机器人"),
        ("HUM", "加湿器"),
        ("MOP", "拖把"),
        ("ETB", "电动牙刷"),
        ("KIT", "烤箱"),
        ("OTH", "其他"),
    )

    CATEGORY = (
        (0, "整机"),
        (1, "配件"),
        (2, "礼品"),
    )

    goods_id = models.CharField(unique=True, max_length=30, verbose_name='货品编码', db_index=True)
    goods_name = models.CharField(unique=True, max_length=60, verbose_name='货品名称', db_index=True)
    category = models.CharField(choices=ATTRIBUTE, default="OTH", max_length=10, verbose_name='货品类别')
    goods_attribute = models.IntegerField(choices=CATEGORY, default=0, verbose_name='货品属性')
    goods_number = models.CharField(unique=True, max_length=10, verbose_name='机器排序')
    size = models.CharField(null=True, blank=True, max_length=50, verbose_name='规格')
    width = models.IntegerField(null=True, blank=True, verbose_name='长')
    height = models.IntegerField(null=True, blank=True, verbose_name='宽')
    depth = models.IntegerField(null=True, blank=True, verbose_name='高')
    weight = models.IntegerField(null=True, blank=True, verbose_name='重量')
    catalog_num = models.CharField(null=True, blank=True, max_length=230, verbose_name='爆炸图号')

    class Meta:
        verbose_name = 'BASE-货品信息表'
        verbose_name_plural = verbose_name
        db_table = 'base_goodsinfo'

    def __str__(self):
        return self.goods_name





class PartInfo(GoodsInfo):
    VERIFY_FIELD = ['goods_id', 'goods_name']

    class Meta:
        verbose_name = 'BASE-配件信息表'
        verbose_name_plural = verbose_name
        proxy = True

    def __str__(self):
        return self.goods_name

    @classmethod
    def verify_mandatory(cls, columns_key):

        for i in cls.VERIFY_FIELD:
            if i not in columns_key:
                return 'verify_field error, must have mandatory field: "{}""'.format(i)
        else:
            return None


class MachineInfo(GoodsInfo):
    class Meta:
        verbose_name = 'BASE-机器信息表'
        verbose_name_plural = verbose_name
        proxy = True

    def __str__(self):
        return self.goods_name








