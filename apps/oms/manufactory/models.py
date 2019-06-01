# -*- coding:  utf-8 -*-
# @Time    :  2019/5/11 13: 47
# @Author  :  Hann
# @Site    :
# @File    :  models.py
# @Software:  PyCharm

from django.db import models
import django.utils.timezone as timezone

from db.base_model import BaseModel
from apps.oms.machine.models import MachineInfo
from tbd2.settings import AUTH_USER_MODEL
from apps.utils.geography.models import CityInfo

class ManufactoryInfo(BaseModel):
    CATEGORY = (
        (0, '整机厂'),
        (1, '配件厂')
    )
    name = models.CharField(unique=True, max_length=60, verbose_name='工厂名称')
    code = models.CharField(unique=True, null=True, blank=True, max_length=20, verbose_name='工厂代码')
    address = models.ForeignKey(CityInfo, on_delete=models.CASCADE, verbose_name='省份')
    category = models.IntegerField(choices=CATEGORY, default=0, verbose_name='工厂类型')
    contacts = models.CharField(max_length=60, verbose_name='联系人')
    contacts_phone = models.CharField(max_length=30, verbose_name='电话')
    memorandum = models.CharField(max_length=150, verbose_name='备注')

    class Meta:
        verbose_name = '工厂信息'
        verbose_name_plural = verbose_name
        db_table = 'oms_manu_manufactory'

    def __str__(self):
        return self.name


class BatchInfo(BaseModel):
    CATEGORY = (
        (0, '未处理'),
        (1, '单据已递交'),
        (2, '单据异常'),
    )
    planorder_id = models.CharField(unique=True, max_length=50, verbose_name='计划采购单号')
    goods_id = models.CharField(max_length=30, verbose_name='货品编码')
    goods_name = models.CharField(max_length=60, verbose_name='货品名称')
    batch_num = models.CharField(max_length=30, verbose_name='批次号')
    quantity = models.IntegerField(verbose_name='下单数量')
    manufactory = models.CharField(max_length=60, verbose_name='工厂名称')
    category = models.IntegerField(choices=CATEGORY, default=0, verbose_name='订单状态')

    class Meta:
        verbose_name = '批次订单'
        verbose_name_plural = verbose_name
        db_table = 'oms_manu_batch'

    def __str__(self):
        return self.batch_num