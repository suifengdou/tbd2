# -*- coding:  utf-8 -*-
# @Time    :  2019/5/11 13: 47
# @Author  :  Hann
# @Site    :
# @File    :  models.py
# @Software:  PyCharm

from django.db import models
import django.utils.timezone as timezone

from db.base_model import BaseModel
from apps.oms.machine.models import MachineInfo, PartInfo, GoodsInfo
from apps.base.manufactory.models import ManufactoryInfo
from apps.base.warehouse.models import WarehouseInfo
from tbd2.settings import AUTH_USER_MODEL
from apps.utils.geography.models import CityInfo


class GoodsToManufactoryInfo(BaseModel):
    STATUS = (
        (0, '正常'),
        (1, '停用'),
    )
    CATEGORY = (
        (0, '整机装配厂'),
        (1, '客供件'),
        (2, '常规配件'),
    )
    goods_name = models.OneToOneField(GoodsInfo, on_delete=models.CASCADE, verbose_name='机器名称')
    manufactory = models.ForeignKey(ManufactoryInfo, on_delete=models.CASCADE, verbose_name='工厂名字')
    status = models.IntegerField(choices=STATUS,  default=0, verbose_name='状态')
    category = models.IntegerField(choices=CATEGORY,  default=0, verbose_name='对照类型')

    class Meta:
        verbose_name = '货品与工厂对照表'
        verbose_name_plural = verbose_name
        db_table = 'base_rel_goods2manufactory'


class MachineToManufactoryInfo(GoodsToManufactoryInfo):

    class Meta:
        verbose_name = '整机工厂对照表'
        verbose_name_plural = verbose_name
        proxy = True


class PartToManufactoryInfo(GoodsToManufactoryInfo):
    class Meta:
        verbose_name = '配件工厂对照表'
        verbose_name_plural = verbose_name
        proxy = True


class CusPartToManufactoryInfo(GoodsToManufactoryInfo):

    class Meta:
        verbose_name = '客供件工厂对照表'
        verbose_name_plural = verbose_name
        proxy = True


class PartToProductInfo(BaseModel):
    STATUS = (
        (0, '正常'),
        (1, '停用'),
    )
    machine_name = models.ForeignKey(MachineInfo, on_delete=models.CASCADE, verbose_name='机器名称')
    part_name = models.ForeignKey(PartInfo, on_delete=models.CASCADE, related_name="parts", verbose_name='配件名称')
    magnification = models.IntegerField(verbose_name='倍率')
    status = models.IntegerField(choices=STATUS, default=0, verbose_name='状态')

    class Meta:
        verbose_name = '客供与机器对照表'
        verbose_name_plural = verbose_name
        db_table = 'base_rel_part2product'


class ManufactoryToWarehouse(BaseModel):
    STATUS = (
        (0, '正常'),
        (1, '停用'),
    )
    manufactory = models.OneToOneField(ManufactoryInfo, on_delete=models.CASCADE, verbose_name='工厂')
    warehouse = models.ForeignKey(WarehouseInfo, on_delete=models.CASCADE, verbose_name='仓库')
    status = models.IntegerField(choices=STATUS, default=0, verbose_name='状态')

    class Meta:
        verbose_name = '工厂与仓库对照表'
        verbose_name_plural = verbose_name
        db_table = 'base_rel_manu2wh'
