# -*- coding:  utf-8 -*-
# @Time    :  2019/5/11 13: 47
# @Author  :  Hann
# @Site    :
# @File    :  models.py
# @Software:  PyCharm

from django.db import models
import django.utils.timezone as timezone

from db.base_model import BaseModel
from apps.base.warehouse.models import WarehouseInfo
from apps.base.goods.models import GoodsInfo


class OriStockOutInfo(BaseModel):

    ORDERSTATUS = (
        (0, '已取消'),
        (1, '未处理'),
        (2, '已完成'),
    )

    MISTAKE_LIST = (
        (0, '正常'),
        (1, '递交重复'),
        (2, '货品非法'),
        (3, '仓库非法'),
        (4, '店铺非法'),
        (5, '先标记为已对账才能审核'),
        (6, '工单必须为取消状态'),
        (7, '先标记为终端清才能审核'),
    )

    order_id = models.CharField(max_length=30, verbose_name='订单编号')
    ori_order_id = models.CharField(max_length=30, verbose_name='子单原始单号')
    sub_order_id = models.CharField(max_length=30, verbose_name='原始子订单号')
    warehouse = models.CharField(max_length=30, verbose_name='仓库')
    shop = models.CharField(max_length=30, verbose_name='店铺')
    status = models.CharField(max_length=30, verbose_name='出库单状态')
    goods_id = models.CharField(max_length=30, verbose_name='商家编码')
    goods_name = models.CharField(max_length=30, verbose_name='货品简称')
    quantity = models.IntegerField(verbose_name='货品数量')
    price = models.FloatField(verbose_name='货品成交价')
    amount = models.FloatField(verbose_name='货品成交总价')
    nickname = models.CharField(max_length=30, verbose_name='客户网名')
    buyer = models.CharField(max_length=30, verbose_name='收件人')
    area = models.CharField(max_length=30, verbose_name='收货地区')
    address = models.CharField(max_length=30, verbose_name='收货地址')
    smartphone = models.CharField(max_length=30, verbose_name='收件人手机')
    deliver_time = models.CharField(max_length=30, verbose_name='发货时间')
    memorandum = models.CharField(max_length=30, verbose_name='买家留言')
    remark = models.CharField(max_length=30, verbose_name='客服备注')

    order_status = models.IntegerField(choices=ORDERSTATUS, default=1, verbose_name='单据状态')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误原因')

    class Meta:
        verbose_name = 'WMS-O-原始出库单'
        verbose_name_plural = verbose_name
        db_table = 'wms_stk_oristockout'

    def __str__(self):
        return self.order_id


class OriSOUnhandle(OriStockOutInfo):

    class Meta:
        verbose_name = 'WMS-O-原始出库单未审核'
        verbose_name_plural = verbose_name
        proxy = True


class StockOutInfo(BaseModel):

    ORDERSTATUS = (
        (0, '已取消'),
        (1, '未处理'),
        (2, '已完成'),
    )

    MISTAKE_LIST = (
        (0, '正常'),
        (1, '递交重复'),
        (2, '货品非法'),
        (3, '仓库非法'),
        (4, '店铺非法'),
        (5, '先标记为已对账才能审核'),
        (6, '工单必须为取消状态'),
        (7, '先标记为终端清才能审核'),
    )

    order_id = models.CharField(max_length=30, verbose_name='订单编号')
    ori_order_id = models.CharField(max_length=30, verbose_name='子单原始单号')
    sub_order_id = models.CharField(max_length=30, verbose_name='原始子订单号')
    warehouse = models.ForeignKey(WarehouseInfo, on_delete=models.CASCADE, verbose_name='仓库')
    shop = models.CharField(max_length=30, verbose_name='店铺')
    status = models.CharField(max_length=30, verbose_name='出库单状态')
    goods_id = models.CharField(max_length=30, verbose_name='商家编码')
    goods_name = models.ForeignKey(GoodsInfo, on_delete=models.CASCADE, verbose_name='货品简称')
    quantity = models.IntegerField(verbose_name='货品数量')
    price = models.FloatField(verbose_name='货品成交价')
    amount = models.FloatField(verbose_name='货品成交总价')
    nickname = models.CharField(max_length=30, verbose_name='客户网名')
    buyer = models.CharField(max_length=30, verbose_name='收件人')
    area = models.CharField(max_length=30, verbose_name='收货地区')
    address = models.CharField(max_length=30, verbose_name='收货地址')
    smartphone = models.CharField(max_length=30, verbose_name='收件人手机')
    deliver_time = models.CharField(max_length=30, verbose_name='发货时间')
    memorandum = models.CharField(max_length=30, verbose_name='买家留言')
    remark = models.CharField(max_length=30, verbose_name='客服备注')

    order_status = models.IntegerField(choices=ORDERSTATUS, default=1, verbose_name='单据状态')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误原因')

    class Meta:
        verbose_name = 'WMS-O-出库单'
        verbose_name_plural = verbose_name
        db_table = 'wms_stk_stockout'

    def __str__(self):
        return self.order_id


class SOUnhandle(StockOutInfo):

    class Meta:
        verbose_name = 'WMS-O-未审核出库单'
        verbose_name_plural = verbose_name
        proxy = True


