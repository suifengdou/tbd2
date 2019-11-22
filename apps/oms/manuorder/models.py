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
from apps.wms.stockin.models import StockInInfo
from apps.base.company.models import ManuInfo




class ManuOrderInfo(BaseModel):

    ORDERSTATUS = (
        (0, '取消'),
        (1, '待处理'),
        (2, '待生产'),
        (3, '在生产'),
        (4, '已完成'),
    )
    batch_num = models.CharField(unique=True, max_length=30, verbose_name='批次号', db_index=True)
    planorder_id = models.CharField(max_length=30, verbose_name='计划采购单号', db_index=True)
    goods_id = models.CharField(max_length=30, verbose_name='货品编码')
    goods_name = models.CharField(max_length=60, verbose_name='货品名称')
    quantity = models.IntegerField(verbose_name='货品数量')
    order_status = models.IntegerField(choices=ORDERSTATUS, default=1, verbose_name='生产单状态')
    manufactory = models.ForeignKey(ManuInfo, on_delete=models.CASCADE, verbose_name='工厂名称')
    estimated_time = models.DateTimeField(verbose_name='期望到货时间')
    start_sn = models.CharField(null=True, max_length=30, verbose_name='首号')
    end_sn = models.CharField(null=True, max_length=30, verbose_name='尾号')

    class Meta:
        verbose_name = 'OMS-M-工厂生产列表'
        verbose_name_plural = verbose_name
        db_table = 'oms_mfo_manuorder'

    def __str__(self):
        return self.batch_num

    def completednum(self):
        completed_num = StockInInfo.objects.filter(batch_num=self.batch_num, order_status=2).aggregate(Sum("quantity"))["quantity__sum"]
        if completed_num:
            if self.order_status == 2:
                self.order_status = 3
                self.save()
            elif completed_num == self.quantity:
                self.order_status = 4
                self.save()
        else:
            completed_num = 0
        return completed_num

    completednum.short_description = '已完成'

    def processingnum(self):
        processing_num = self.qcoriinfo_set.all().filter(order_status=1, result=0).aggregate(Sum("quantity"))["quantity__sum"]
        if not processing_num:
            processing_num = 0
        return processing_num
    processingnum.short_description = '验货中'

    def failurenum(self):
        failure_num = self.qcoriinfo_set.all().filter(order_status__in=[1, 2], result=1).aggregate(Sum("quantity"))["quantity__sum"]
        if failure_num is None:
            failure_num = 0
        return failure_num
    failurenum.short_description = '验货失败'

    def penddingnum(self):
        pending_num = int(self.quantity) - int(self.processingnum()) - int(self.intransitnum())
        return pending_num
    penddingnum.short_description = '待生产'

    def intransitnum(self):
        intransit_num = StockInInfo.objects.filter(batch_num=self.batch_num, order_status__in=[1, 2]).aggregate(Sum("quantity"))["quantity__sum"]
        if not intransit_num:
            intransit_num = 0
        return intransit_num
    intransitnum.short_description = '入库合计'


class ManuOrderPenddingInfo(ManuOrderInfo):

    class Meta:
        verbose_name = 'OMS-M-待客供生产列表'
        verbose_name_plural = verbose_name
        proxy = True


class ManuOrderProcessingInfo(ManuOrderInfo):
    class Meta:
        verbose_name = 'OMS-M-待生产列表'
        verbose_name_plural = verbose_name
        proxy = True



