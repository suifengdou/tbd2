# -*- coding:  utf-8 -*-
# @Time    :  2019/5/11 13: 47
# @Author  :  Hann
# @Site    :
# @File    :  models.py
# @Software:  PyCharm

from django.db import models
import django.utils.timezone as timezone
from django.db.models import Sum, Avg, Min, Max

from db.base_model import BaseModel
from apps.wms.stock.models import StockInOrderInfo
from apps.base.manufactory.models import ManufactoryInfo


class ManuOrderInfo(BaseModel):

    ORDERSTATUS = (
        (0, '取消'),
        (1, '待处理'),
        (2, '已确认'),
        (3, '在生产'),
        (4, '已完成'),
    )
    batch_num = models.CharField(unique=True, max_length=30, verbose_name='批次号', db_index=True)
    planorder_id = models.CharField(unique=True, max_length=30, verbose_name='计划采购单号', db_index=True)
    goods_id = models.CharField(max_length=30, verbose_name='货品编码')
    goods_name = models.CharField(max_length=60, verbose_name='货品名称')
    quantity = models.IntegerField(verbose_name='货品数量')
    status = models.IntegerField(choices=ORDERSTATUS, default=0, verbose_name='生产单状态')
    manufactory = models.ForeignKey(ManufactoryInfo, on_delete=models.CASCADE, verbose_name='工厂名称')
    estimated_time = models.DateTimeField(verbose_name='期望到货时间')
    start_sn = models.CharField(null=True, max_length=30, verbose_name='首号')
    end_sn = models.CharField(null=True, max_length=30, verbose_name='尾号')

    class Meta:
        verbose_name = '工厂生产列表'
        verbose_name_plural = verbose_name
        db_table = 'oms_mfo_manuorder'

    def __str__(self):
        return self.batch_num

    def completednum(self):
        completed_num = StockInOrderInfo.objects.filter(batch_num=self.batch_num).aggregate(Sum("quantity"))["quantity__sum"]
        return completed_num

    completednum.short_description = '已完成数量'


class ManuOrderPenddingInfo(ManuOrderInfo):

    class Meta:
        verbose_name = '待客供生产列表'
        verbose_name_plural = verbose_name
        proxy = True


class ManuOrderProcessingInfo(ManuOrderInfo):
    class Meta:
        verbose_name = '待生产列表'
        verbose_name_plural = verbose_name
        proxy = True


