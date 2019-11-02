# -*- coding:  utf-8 -*-
# @Time    :  2019/5/11 13: 47
# @Author  :  Hann
# @Site    :
# @File    :  models.py
# @Software:  PyCharm

from django.db import models
import django.utils.timezone as timezone

from db.base_model import BaseModel
from apps.oms.manuorder.models import ManuOrderInfo
from django.db.models import Count, Avg, Max, Min, Sum
from apps.base.warehouse.models import WarehouseInfo


class QCOriInfo(BaseModel):
    ORDERSTATUS = (
        (0, '已取消'),
        (1, '未递交'),
        (2, '已递交'),
        (3, '异常'),
    )
    RESULT = (
        (0, '合格'),
        (1, '不合格'),
    )
    CATEGORY = (
        (0, '首检'),
        (1, '复检'),
        (2, '召回'),
    )
    ERROR_LIST = (
        (0, '正常'),
        (1, '质检数超订单数'),
        (2, '工厂没关联仓库'),
        (3, '已存在入库单，请联系管理员处理'),
        (4, '生入库单出现意外'),
        (5, '已递交过，检查处理'),
        (6, '递交质检单出现意外'),
    )

    batch_num = models.ForeignKey(ManuOrderInfo, on_delete=models.CASCADE, verbose_name='批次号码')
    order_status = models.SmallIntegerField(choices=ORDERSTATUS, default=1, verbose_name='质检单状态')
    quantity = models.IntegerField(verbose_name='验货数量')
    result = models.SmallIntegerField(choices=RESULT, default=0, verbose_name='验货结果')
    category = models.SmallIntegerField(choices=CATEGORY, default=0, verbose_name='验货类型')
    check_quantity = models.IntegerField(verbose_name='抽检数量')
    a_flaw = models.IntegerField(verbose_name='A类缺陷')
    b1_flaw = models.IntegerField(verbose_name='B1类缺陷')
    b2_flaw = models.IntegerField(verbose_name='B2类缺陷')
    c_flaw = models.IntegerField(verbose_name='C类缺陷')
    memorandum = models.CharField(null=True, blank=True, max_length=200, verbose_name='备注')
    qc_order_id = models.CharField(null=True, max_length=30, verbose_name='质检单号')
    error_info = models.SmallIntegerField(choices=ERROR_LIST, default=0, verbose_name='错误原因')
    qc_time = models.DateTimeField(default=timezone.now, verbose_name='质检时间')

    class Meta:
        verbose_name = 'OMS-QC-原始质检单明细表'
        verbose_name_plural = verbose_name
        db_table = 'oms_qc_oriorder'

    def __str__(self):
        return str(self.quantity)


class QCSubmitOriInfo(QCOriInfo):

    class Meta:
        verbose_name = 'OMS-QC-未递交原始质检单'
        verbose_name_plural = verbose_name
        proxy = True


class QCInfo(BaseModel):
    ORDERSTATUS = (
        (0, '已取消'),
        (1, '未处理'),
        (2, '已确认'),
        (3, '已递交'),
        (4, '异常'),
    )
    RESULT = (
        (0, '合格'),
        (1, '不合格'),
    )
    CATEGORY = (
        (0, '首检'),
        (1, '复检'),
        (2, '召回'),
    )

    batch_num = models.ForeignKey(ManuOrderInfo, on_delete=models.CASCADE, verbose_name='批次号码')
    warehouse = models.ForeignKey(WarehouseInfo, on_delete=models.CASCADE, verbose_name='仓库名称')
    qc_order_id = models.CharField(unique=True, max_length=30, verbose_name='质检单号')
    goods_name = models.CharField(max_length=60, verbose_name='货品名称')
    order_status = models.IntegerField(choices=ORDERSTATUS, default=1, verbose_name='质检单状态')
    manufactory = models.CharField(max_length=60, verbose_name='工厂名称')
    goods_id = models.CharField(max_length=30, verbose_name='货品编码')

    quantity = models.IntegerField(verbose_name='验货数量')
    total_quantity = models.IntegerField(verbose_name='订单数量')
    accumulation = models.IntegerField(verbose_name='累计数量')
    result = models.IntegerField(choices=RESULT, verbose_name='验货结果')
    category = models.IntegerField(choices=CATEGORY, verbose_name='验货类型')
    check_quantity = models.IntegerField(verbose_name='抽检数量')
    a_flaw = models.IntegerField(verbose_name='A类缺陷')
    b1_flaw = models.IntegerField(verbose_name='B1类缺陷')
    b2_flaw = models.IntegerField(verbose_name='B2类缺陷')
    c_flaw = models.IntegerField(verbose_name='C类缺陷')
    memorandum = models.CharField(null=True, blank=True, max_length=200, verbose_name='备注')
    qc_time = models.DateTimeField(verbose_name='验货时间')


    class Meta:
        verbose_name = 'OMS-QC-质检单明细表'
        verbose_name_plural = verbose_name
        db_table = 'oms_qc_order'


class QCSubmitInfo(QCInfo):

    class Meta:
        verbose_name = 'OMS-QC-未递交质检单明细表'
        verbose_name_plural = verbose_name
        proxy = True