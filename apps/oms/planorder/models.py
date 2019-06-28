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
from apps.oms.machine.models import MachineInfo, PartInfo
from apps.wms.stock.models import StockInfo
from apps.base.manufactory.models import ManufactoryInfo


class PlanOrderInfo(BaseModel):
    ORDERSTATUS = (
        (0, '取消'),
        (1, '未处理'),
        (2, '待确认'),
        (3, '异常'),
        (4, '已递交'),
    )
    CATEGORY = (
        (0, '常规'),
        (1, '加急'),
        (2, '大促'),
    )

    planorder_id = models.CharField(null=True, blank=True, unique=True, max_length=30, verbose_name="计划采购单号", db_index=True)
    goods_name = models.ForeignKey(MachineInfo, on_delete=models.CASCADE, verbose_name='机器名称')
    quantity = models.IntegerField(verbose_name='订单数量')
    estimated_time = models.DateTimeField(verbose_name='期望到货时间')
    status = models.IntegerField(choices=ORDERSTATUS, default=1, verbose_name='计划采购单状态')
    category = models.IntegerField(choices=CATEGORY, default=0, verbose_name='订单类型')

    class Meta:
        verbose_name = '整机采购申请单'
        verbose_name_plural = verbose_name
        db_table = 'oms_po_order'


class PlanOrderPenddingInfo(PlanOrderInfo):

    class Meta:
        verbose_name = '未处理计划单'
        verbose_name_plural = verbose_name
        proxy = True


class PlanOrderSubmitInfo(PlanOrderInfo):
    class Meta:
        verbose_name = '未递交计划单'
        verbose_name_plural = verbose_name
        proxy = True


class CusRequisitionInfo(BaseModel):
    ORDERSTATUS = (
        (0, '取消'),
        (1, '未处理'),
        (2, '异常'),
        (3, '已递交'),
    )
    planorder_id = models.CharField(max_length=30, verbose_name='计划采购单号', db_index=True)
    batch_num = models.CharField(max_length=30, verbose_name='批次号', db_index=True)
    goods_id = models.CharField(max_length=30, verbose_name='货品编码')
    goods_name = models.CharField(max_length=60, verbose_name='货品名称')
    quantity = models.IntegerField(verbose_name='货品数量')

    estimated_time = models.DateTimeField(verbose_name='期望到货时间')
    status = models.IntegerField(choices=ORDERSTATUS, default=1, verbose_name='需求单单状态')
    manufactory = models.ForeignKey(ManufactoryInfo, on_delete=models.CASCADE, null=True, blank=True, verbose_name='工厂名称')
    cus_requisition_id = models.CharField(null=True, blank=True, unique=True, max_length=30, verbose_name='需求单号')

    class Meta:
        verbose_name = '需求单'
        verbose_name_plural = verbose_name
        db_table = 'oms_po_crorder'

    def available_inventory(self):
        available_inventory = StockInfo.objects.filter(goods_id=self.goods_id)
        if available_inventory:
            available_inventory = available_inventory[0].available_inventory()
        else:
            available_inventory = 0
        return available_inventory
    available_inventory.short_description = "可用库存"

    def __str__(self):
        return self.cus_requisition_id


class CusRequisitionSubmitInfo(CusRequisitionInfo):
    class Meta:
        verbose_name = '未递交需求单'
        verbose_name_plural = verbose_name
        proxy = True


class CusPartOrderInfo(BaseModel):
    CATEGORY = (
        (0, '常规'),
        (1, '加急'),
        (2, '大促'),
    )
    ORDER_ATTRIBUTE = (
        (0, '配件采购单'),
        (1, '客供件采购单'),
    )
    ORDERSTATUS = (
        (0, '取消'),
        (1, '未处理'),
        (2, '已确认'),
        (3, '已递交'),
    )

    planorder_id = models.CharField(null=True, blank=True, unique=True, max_length=30, verbose_name='计划采购单号')
    goods_name = models.ForeignKey(PartInfo, on_delete=models.CASCADE, verbose_name='配件名称')
    quantity = models.IntegerField(verbose_name='采购数量')
    estimated_time = models.DateTimeField(verbose_name='期望到货时间')
    status = models.IntegerField(choices=ORDERSTATUS, default=1, verbose_name='采购单状态')
    category = models.IntegerField(choices=CATEGORY, default=0, verbose_name='采购单类别')
    order_attribute = models.IntegerField(choices=ORDER_ATTRIBUTE, default=0, verbose_name='采购单类别')
    source_order_id = models.ForeignKey(CusRequisitionInfo, on_delete=models.CASCADE, null=True, blank=True, verbose_name='来源单号')
    manufactory = models.ForeignKey(ManufactoryInfo, on_delete=models.CASCADE, null=True, blank=True,
                                    verbose_name='工厂名称')

    class Meta:
        verbose_name = '非整机采购申请单'
        verbose_name_plural = verbose_name
        db_table = 'oms_po_csorder'





