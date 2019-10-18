# -*- coding:  utf-8 -*-
# @Time    :  2019/5/11 13: 47
# @Author  :  Hann
# @Site    :
# @File    :  models.py
# @Software:  PyCharm

from django.db import models
import django.utils.timezone as timezone


from db.base_model import BaseModel
from apps.base.goods.models import PartInfo
from apps.oms.cusrequisition.models import CusRequisitionInfo
from apps.base.company.models import ManuInfo


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
        (0, '已取消'),
        (1, '未处理'),
        (2, '已确认'),
        (3, '已入库'),
        (4, '异常'),
    )

    planorder_id = models.CharField(null=True, blank=True, unique=True, max_length=30, verbose_name='计划采购单号')
    goods_name = models.ForeignKey(PartInfo, on_delete=models.CASCADE, verbose_name='配件名称')
    quantity = models.IntegerField(verbose_name='采购数量')
    estimated_time = models.DateTimeField(verbose_name='期望到货时间')
    order_status = models.IntegerField(choices=ORDERSTATUS, default=1, verbose_name='采购单状态')
    category = models.IntegerField(choices=CATEGORY, default=0, verbose_name='采购单类别')
    order_attribute = models.IntegerField(choices=ORDER_ATTRIBUTE, default=0, verbose_name='采购单类别')
    source_order_id = models.ForeignKey(CusRequisitionInfo, on_delete=models.CASCADE, null=True, blank=True, verbose_name='来源单号')
    manufactory = models.ForeignKey(ManuInfo, on_delete=models.CASCADE, null=True, blank=True,
                                    verbose_name='工厂名称')

    class Meta:
        verbose_name = 'OMS-CP-非整机采购申请单'
        verbose_name_plural = verbose_name
        db_table = 'oms_pp_purchaseorder'


class CusPartPenddingOrderInfo(CusPartOrderInfo):

    class Meta:
        verbose_name = 'OMS-CP-未审核非整机采购申请单'
        verbose_name_plural = verbose_name
        proxy = True


class CusPartProductOrderInfo(CusPartOrderInfo):

    class Meta:
        verbose_name = 'OMS-CP-在生产非整机采购申请单'
        verbose_name_plural = verbose_name
        proxy = True

