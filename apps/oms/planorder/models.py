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


class PlanOrderInfo(BaseModel):
    ORDERSTATUS = (
        (0, '未处理'),
        (1, '已递交'),
        (1, '已确认'),
        (2, '异常'),
    )
    CATEGORY = (
        (0, '常规'),
        (1, '加急'),
        (2, '大促'),
    )

    planorder_id = models.CharField(unique=True, max_length=50, verbose_name="计划采购单号")
    goods_name = models.ForeignKey(MachineInfo, on_delete=models.CASCADE, verbose_name='机器名称')
    quantity = models.IntegerField(verbose_name='订单数量')
    estimated_time = models.DateTimeField(verbose_name='期望到货时间')
    feedback_time = models.DateTimeField(null=True, blank=True, verbose_name='反馈到货时间')
    order_status = models.IntegerField(choices=ORDERSTATUS, default=0, verbose_name='计划采购单状态')
    category = models.IntegerField(choices=CATEGORY, default=0, verbose_name='订单类型')


class CusPartOrderInfo(BaseModel):
    CATEGORY = (
        (0, '客供件采购单'),
        (1, '配件采购单'),
    )
    STATUS = (
        (0, '未处理'),
        (1, '已审核'),
        (2, '部分到货'),
        (3, '已到货'),
        (4, '已取消'),
    )

    cus_planorder_id = models.CharField(unique=True, max_length=30, verbose_name='客供计划单采购单号')
    part_name = models.ForeignKey(PartInfo, on_delete=models.CASCADE, verbose_name='配件名称')
    quantity = models.IntegerField(verbose_name='采购数量')
    category = models.IntegerField(choices=CATEGORY, default=0, verbose_name='采购单类别')
    status = models.IntegerField(choices=STATUS, default=0, verbose_name='采购单状态')
