# -*- coding:  utf-8 -*-
# @Time    :  2019/5/11 13: 47
# @Author  :  Hann
# @Site    :
# @File    :  models.py
# @Software:  PyCharm


from django.db import models


from db.base_model import BaseModel
from apps.base.company.models import ManuInfo
from apps.wms.stock.models import StockInfo


class CusRequisitionInfo(BaseModel):
    ORDERSTATUS = (
        (0, '已取消'),
        (1, '未处理'),
        (2, '已递交'),
        (3, '异常'),
    )
    planorder_id = models.CharField(max_length=30, verbose_name='计划采购单号', db_index=True)
    batch_num = models.CharField(max_length=30, verbose_name='批次号', db_index=True)
    goods_id = models.CharField(max_length=30, verbose_name='货品编码')
    goods_name = models.CharField(max_length=60, verbose_name='货品名称')
    quantity = models.IntegerField(verbose_name='货品数量')

    estimated_time = models.DateTimeField(verbose_name='期望到货时间')
    order_status = models.IntegerField(choices=ORDERSTATUS, default=1, verbose_name='需求单单状态')
    manufactory = models.ForeignKey(ManuInfo, on_delete=models.CASCADE, null=True, blank=True, verbose_name='工厂名称')
    cus_requisition_id = models.CharField(null=True, blank=True, unique=True, max_length=30, verbose_name='需求单号')

    class Meta:
        verbose_name = 'OMS-R-需求单'
        verbose_name_plural = verbose_name
        db_table = 'oms_cr_requisition'

    def available_quantity(self):
        available_quantity = StockInfo.objects.filter(goods_id=self.goods_id)
        if available_quantity:
            available_quantity = available_quantity[0].available_quantity()
        else:
            available_quantity = 0
        return available_quantity
    available_quantity.short_description = "可用库存"

    def __str__(self):
        return self.cus_requisition_id


class CusRequisitionSubmitInfo(CusRequisitionInfo):
    class Meta:
        verbose_name = 'OMS-R-未递交需求单'
        verbose_name_plural = verbose_name
        proxy = True