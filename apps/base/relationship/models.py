# -*- coding:  utf-8 -*-
# @Time    :  2019/5/11 13: 47
# @Author  :  Hann
# @Site    :
# @File    :  models.py
# @Software:  PyCharm

from django.db import models
import django.utils.timezone as timezone

from db.base_model import BaseModel
from apps.base.goods.models import MachineInfo, PartInfo, GoodsInfo
from apps.base.company.models import ManuInfo
from apps.base.warehouse.models import WarehouseInfo

from apps.utils.geography.models import CityInfo
from apps.oms.qcorder.models import QCOriInfo
from apps.oms.manuorder.models import ManuOrderInfo


class GoodsToManufactoryInfo(BaseModel):

    VERIFY_FIELD = ['goods_id', 'manufactory']

    STATUS = (
        (0, '停用'),
        (1, '正常'),
    )
    CATEGORY = (
        (0, '整机装配厂'),
        (1, '常规配件'),
    )
    goods_name = models.OneToOneField(GoodsInfo, on_delete=models.CASCADE, verbose_name='机器名称')
    manufactory = models.ForeignKey(ManuInfo, on_delete=models.CASCADE, verbose_name='工厂名字')
    status = models.IntegerField(choices=STATUS,  default=1, verbose_name='状态')
    category = models.IntegerField(choices=CATEGORY,  default=0, verbose_name='对照类型')

    class Meta:
        verbose_name = 'BA-R-全部货品与工厂对照表'
        verbose_name_plural = verbose_name
        db_table = 'base_rel_goods2manufactory'

    @classmethod
    def verify_mandatory(cls, columns_key):

        for i in cls.VERIFY_FIELD:
            if i not in columns_key:
                return 'verify_field error, must have mandatory field: "{}""'.format(i)
        else:
            return None



class MachineToManufactoryInfo(GoodsToManufactoryInfo):

    class Meta:
        verbose_name = 'BA-R-整机工厂对照表'
        verbose_name_plural = verbose_name
        proxy = True


class PartToManufactoryInfo(GoodsToManufactoryInfo):
    class Meta:
        verbose_name = 'BA-R-配件工厂对照表'
        verbose_name_plural = verbose_name
        proxy = True


class CusPartToManufactoryInfo(GoodsToManufactoryInfo):

    class Meta:
        verbose_name = 'BA-R-客供件工厂对照表'
        verbose_name_plural = verbose_name
        proxy = True


class PartToProductInfo(BaseModel):
    STATUS = (
        (0, '停用'),
        (1, '正常'),
    )
    machine_name = models.ForeignKey(MachineInfo, on_delete=models.CASCADE, verbose_name='机器名称')
    part_name = models.ForeignKey(PartInfo, on_delete=models.CASCADE, related_name="parts", verbose_name='配件名称')
    magnification = models.IntegerField(verbose_name='倍率')
    status = models.IntegerField(choices=STATUS, default=1, verbose_name='状态')

    class Meta:
        verbose_name = 'BA-R-客供与机器对照表'
        verbose_name_plural = verbose_name
        db_table = 'base_rel_part2product'


class ManufactoryToWarehouse(BaseModel):
    STATUS = (
        (0, '停用'),
        (1, '正常'),
    )
    manufactory = models.OneToOneField(ManuInfo, on_delete=models.CASCADE, verbose_name='工厂')
    warehouse = models.ForeignKey(WarehouseInfo, on_delete=models.CASCADE, verbose_name='仓库')
    status = models.IntegerField(choices=STATUS, default=1, verbose_name='状态')

    class Meta:
        verbose_name = 'BA-R-工厂与仓库对照表'
        verbose_name_plural = verbose_name
        db_table = 'base_rel_manu2wh'
