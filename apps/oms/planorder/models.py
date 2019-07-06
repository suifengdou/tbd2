# -*- coding:  utf-8 -*-
# @Time    :  2019/5/11 13: 47
# @Author  :  Hann
# @Site    :
# @File    :  models.py
# @Software:  PyCharm

from django.db import models
import django.utils.timezone as timezone

from db.base_model import BaseModel
from tbd2.settings import AUTH_USER_MODEL
from apps.base.goods.models import MachineInfo, PartInfo
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
        verbose_name = 'OMS-P-整机采购申请单'
        verbose_name_plural = verbose_name
        db_table = 'oms_po_order'


class PlanOrderPenddingInfo(PlanOrderInfo):

    class Meta:
        verbose_name = 'OMS-P-未处理计划单'
        verbose_name_plural = verbose_name
        proxy = True


class PlanOrderSubmitInfo(PlanOrderInfo):
    class Meta:
        verbose_name = 'OMS-P-未递交计划单'
        verbose_name_plural = verbose_name
        proxy = True







