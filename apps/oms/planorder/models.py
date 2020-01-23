# -*- coding:  utf-8 -*-
# @Time    :  2019/5/11 13: 47
# @Author  :  Hann
# @Site    :
# @File    :  models.py
# @Software:  PyCharm

from django.db import models
import django.utils.timezone as timezone

from db.base_model import BaseModel
from apps.base.goods.models import MachineInfo, PartInfo
from apps.wms.stock.models import StockInfo


class OriPlanOrderInfo(BaseModel):
    ORDERSTATUS = (
        (0, '取消'),
        (1, '未处理'),
        (2, '已递交'),
    )
    CATEGORY = (
        (0, '常规'),
        (1, '加急'),
        (2, '大促'),
    )
    TAG_SIGN = (
        (0, '正常'),
        (1, '重复递交'),
        (2, '有已经取消的计划单'),
        (3, '货品非法'),
        (4, '保存单据出错'),
    )

    planorder_id = models.CharField(unique=True, max_length=30, verbose_name="计划采购单号")
    goods_name = models.CharField(max_length=30, verbose_name='机器名称', db_index=True)
    quantity = models.IntegerField(verbose_name='订单数量')
    estimated_time = models.DateTimeField(verbose_name='期望到货时间')
    order_status = models.IntegerField(choices=ORDERSTATUS, default=1, verbose_name='计划采购单状态', db_index=True)
    category = models.IntegerField(choices=CATEGORY, default=0, verbose_name='订单类型')
    tag_sign = models.SmallIntegerField(choices=TAG_SIGN, default=0, verbose_name='错误原因')

    class Meta:
        verbose_name = 'OMS-P-原始整机计划单'
        verbose_name_plural = verbose_name
        db_table = 'oms_po_oriorder'


class OriPlanOrderSubmitInfo(OriPlanOrderInfo):
    VERIFY_FIELD = ['planorder_id', 'estimated_time', 'quantity', 'goods_name']

    class Meta:
        verbose_name = 'OMS-P-原始整机计划单未递交'
        verbose_name_plural = verbose_name
        proxy = True

    @classmethod
    def verify_mandatory(cls, columns_key):

        for i in cls.VERIFY_FIELD:
            if i not in columns_key:
                return 'verify_field error, must have mandatory field: "{}""'.format(i)
        else:
            return None


class PlanOrderInfo(BaseModel):
    ORDERSTATUS = (
        (0, '取消'),
        (1, '未处理'),
        (2, '待确认'),
        (3, '已递交'),
        (4, '异常'),
    )
    CATEGORY = (
        (0, '常规'),
        (1, '加急'),
        (2, '大促'),
    )
    TAG_SIGN = (
        (0, '正常'),
        (1, '重复递交'),
        (2, '系统错误'),
        (3, '货品未关联工厂'),
        (4, '保存单据出错'),
    )

    planorder_id = models.CharField(null=True, blank=True, unique=True, max_length=30, verbose_name="计划采购单号", db_index=True)
    goods_name = models.ForeignKey(MachineInfo, on_delete=models.CASCADE, verbose_name='机器名称')
    quantity = models.IntegerField(verbose_name='订单数量')
    estimated_time = models.DateTimeField(verbose_name='期望到货时间')
    order_status = models.IntegerField(choices=ORDERSTATUS, default=1, verbose_name='计划采购单状态')
    category = models.IntegerField(choices=CATEGORY, default=0, verbose_name='订单类型')
    tag_sign = models.SmallIntegerField(choices=TAG_SIGN, default=0, verbose_name='错误原因')

    class Meta:
        verbose_name = 'OMS-P-整机计划单'
        verbose_name_plural = verbose_name
        db_table = 'oms_po_order'


class PlanOrderPenddingInfo(PlanOrderInfo):
    VERIFY_FIELD = ["planorder_id", "goods_id", "quantity", "estimated_time"]

    class Meta:
        verbose_name = 'OMS-P-整机计划单未处理'
        verbose_name_plural = verbose_name
        proxy = True

    @classmethod
    def verify_mandatory(cls, columns_key):

        for i in cls.VERIFY_FIELD:
            if i not in columns_key:
                return 'verify_field error, must have mandatory field: "{}""'.format(i)
        else:
            return None


class PlanOrderSubmitInfo(PlanOrderInfo):
    class Meta:
        verbose_name = 'OMS-P-整机计划单未递交'
        verbose_name_plural = verbose_name
        proxy = True







