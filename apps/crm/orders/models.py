# -*- coding:  utf-8 -*-
# @Time    :  2018/11/26 13: 47
# @Author  :  Hann
# @Site    : 
# @File    :  urls.py.py
# @Software:  PyCharm


from django.db import models

from db.base_model import BaseModel


class OriOrderInfo(BaseModel):

    VERIFY_FIELD = ['buyer_nick', 'trade_no', 'receiver_name', 'receiver_address', 'receiver_mobile',
                    'deliver_time', 'pay_time', 'receiver_area', 'logistics_no', 'buyer_message', 'cs_remark',
                    'src_tids', 'num', 'price', 'share_amount', 'goods_name', 'spec_code', 'order_category',
                    'shop_name', 'logistics_name', 'warehouse_name']

    ORDERSTATUS = (
        (0, '已取消'),
        (1, '未处理'),
        (2, '已完成'),
    )
    MISTAKE_LIST = (
        (0, '正常'),
        (1, '待确认重复订单'),

    )
    PROCESS_TAG = (
        (0, '未处理'),
        (1, '待核实'),
        (2, '已确认'),
        (3, '待清账'),
        (4, '已处理'),
        (5, '特殊订单'),
    )
    ORDER_CATEGORY = (
        (1, "网店销售"),
        (2, "线下零售"),
        (3, "售后换货"),
        (4, "批发业务"),
        (5, "保修换新"),
        (6, "保修完成"),
        (7, "订单补发"),
        (101, "干线调拨"),
    )

    buyer_nick = models.CharField(max_length=150, db_index=True, verbose_name='客户网名')
    trade_no = models.CharField(max_length=60, db_index=True, verbose_name='订单编号')
    receiver_name = models.CharField(max_length=150, verbose_name='收件人')
    receiver_address = models.CharField(max_length=256, verbose_name='收货地址')
    receiver_mobile = models.CharField(max_length=40, db_index=True, verbose_name='收件人手机')
    pay_time = models.DateTimeField(verbose_name='付款时间')
    receiver_area = models.CharField(max_length=150, verbose_name='收货地区')
    logistics_no = models.CharField(null=True, blank=True, max_length=150, verbose_name='物流单号')
    buyer_message = models.TextField(null=True, blank=True, verbose_name='买家留言')
    cs_remark = models.TextField(null=True, blank=True, max_length=800, verbose_name='客服备注')
    src_tids = models.TextField(null=True, blank=True, verbose_name='原始子订单号')
    num = models.IntegerField(verbose_name='货品数量')
    price = models.FloatField(verbose_name='成交价')
    share_amount = models.FloatField(verbose_name='货品成交总价')
    goods_name = models.CharField(max_length=255, verbose_name='货品名称')
    spec_code = models.CharField(max_length=150, verbose_name='商家编码', db_index=True)
    shop_name = models.CharField(max_length=128, verbose_name='店铺')
    logistics_name = models.CharField(null=True, blank=True, max_length=60, verbose_name='物流公司')
    warehouse_name = models.CharField(max_length=100, verbose_name='仓库')
    order_category = models.CharField(max_length=40, db_index=True,  verbose_name='订单类型')
    deliver_time = models.DateTimeField(verbose_name='发货时间', db_index=True)

    order_status = models.SmallIntegerField(choices=ORDERSTATUS, default=1, db_index=True, verbose_name='单据状态')
    process_tag = models.SmallIntegerField(choices=PROCESS_TAG, default=0, verbose_name='处理标签')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误列表')

    class Meta:
        verbose_name = 'CRM-原始订单-查询'
        verbose_name_plural = verbose_name
        db_table = 'crm_o_oriorderinfo'

    def __str__(self):
        return str(self.trade_no)

    @classmethod
    def verify_mandatory(cls, columns_key):
        for i in cls.VERIFY_FIELD:
            if i not in columns_key:
                return 'verify_field error, must have mandatory field: "{}""'.format(i)
        else:
            return None


class SubmitOriOrder(OriOrderInfo):
    class Meta:
        verbose_name = 'CRM-原始订单-未提交'
        verbose_name_plural = verbose_name
        proxy = True


class OrderInfo(BaseModel):

    VERIFY_FIELD = ['buyer_nick', 'trade_no', 'receiver_name', 'receiver_address', 'receiver_mobile',
                    'deliver_time', 'pay_time', 'receiver_area', 'logistics_no', 'buyer_message', 'cs_remark',
                    'src_tids', 'num', 'price', 'share_amount', 'goods_name', 'spec_code', 'order_category',
                    'shop_name', 'logistics_name', 'warehouse_name']

    ORDERSTATUS = (
        (0, '已取消'),
        (1, '未处理'),
        (2, '已完成'),
    )
    MISTAKE_LIST = (
        (0, '正常'),
        (1, '14天内重复订单'),

    )
    PROCESS_TAG = (
        (0, '未处理'),
        (1, '待核实'),
        (2, '已确认'),
        (3, '待清账'),
        (4, '已处理'),
        (5, '特殊订单'),
    )
    ORDER_CATEGORY = (
        (1, "网店销售"),
        (2, "线下零售"),
        (3, "售后换货"),
        (4, "批发业务"),
        (5, "保修换新"),
        (6, "保修完成"),
        (7, "订单补发"),
        (101, "干线调拨"),
    )

    buyer_nick = models.CharField(max_length=150, db_index=True, verbose_name='客户网名')
    trade_no = models.CharField(max_length=60, db_index=True, verbose_name='订单编号')
    receiver_name = models.CharField(max_length=150, verbose_name='收件人')
    receiver_address = models.CharField(max_length=256, verbose_name='收货地址')
    receiver_mobile = models.CharField(max_length=40, db_index=True, verbose_name='收件人手机')
    pay_time = models.DateTimeField(verbose_name='付款时间')
    receiver_area = models.CharField(max_length=150, verbose_name='收货地区')
    logistics_no = models.CharField(null=True, blank=True, max_length=150, verbose_name='物流单号')
    buyer_message = models.TextField(null=True, blank=True, verbose_name='买家留言')
    cs_remark = models.TextField(null=True, blank=True, max_length=800, verbose_name='客服备注')
    src_tids = models.TextField(null=True, blank=True, verbose_name='原始子订单号')
    num = models.IntegerField(verbose_name='实发数量')
    price = models.FloatField(verbose_name='成交价')
    share_amount = models.FloatField(verbose_name='货品成交总价')
    goods_name = models.CharField(max_length=255, verbose_name='货品名称')
    spec_code = models.CharField(max_length=150, verbose_name='商家编码', db_index=True)
    shop_name = models.CharField(max_length=128, verbose_name='店铺')
    logistics_name = models.CharField(null=True, blank=True, max_length=60, verbose_name='物流公司')
    warehouse_name = models.CharField(max_length=100, verbose_name='仓库')
    order_category = models.CharField(max_length=40, db_index=True,  verbose_name='订单类型')
    deliver_time = models.DateTimeField(verbose_name='发货时间', db_index=True)

    order_status = models.SmallIntegerField(choices=ORDERSTATUS, default=1, db_index=True, verbose_name='单据状态')
    process_tag = models.SmallIntegerField(choices=PROCESS_TAG, default=0, verbose_name='处理标签')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误列表')

    class Meta:
        verbose_name = 'CRM-UT订单-查询'
        verbose_name_plural = verbose_name
        db_table = 'crm_o_orderinfo'

    def __str__(self):
        return str(self.trade_no)

    @classmethod
    def verify_mandatory(cls, columns_key):
        for i in cls.VERIFY_FIELD:
            if i not in columns_key:
                return 'verify_field error, must have mandatory field: "{}""'.format(i)
        else:
            return None


class SubmitOrder(OrderInfo):
    class Meta:
        verbose_name = 'CRM-UT订单-未提交'
        verbose_name_plural = verbose_name
        proxy = True


class CheckOrder(OrderInfo):
    class Meta:
        verbose_name = 'CRM-UT订单-未过滤'
        verbose_name_plural = verbose_name
        proxy = True





class SimpleOrderInfo(BaseModel):
    ORDERSTATUS = (
        (0, '已取消'),
        (1, '未处理'),
        (2, '已完成'),
    )
    MISTAKE_LIST = (
        (0, '货品名称错误'),
        (1, '14天内重复订单'),

    )
    PROCESS_TAG = (
        (0, '未处理'),
        (1, '待核实'),
        (2, '已确认'),
        (3, '待清账'),
        (4, '已处理'),
        (5, '特殊订单'),
    )
    ori_order = models.ForeignKey(OriOrderInfo, on_delete=models.CASCADE, verbose_name='源订单')
    buyer_nick = models.CharField(max_length=150, db_index=True, verbose_name='客户网名')
    receiver_name = models.CharField(max_length=150, verbose_name='收件人')
    receiver_address = models.CharField(max_length=256, verbose_name='收货地址')
    receiver_mobile = models.CharField(max_length=40, db_index=True, verbose_name='收件人手机')
    receiver_area = models.CharField(max_length=150, verbose_name='收货地区')

    order_status = models.SmallIntegerField(choices=ORDERSTATUS, default=1, db_index=True, verbose_name='单据状态')
    process_tag = models.SmallIntegerField(choices=PROCESS_TAG, default=0, verbose_name='处理标签')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误列表')

    class Meta:
        verbose_name = 'CRM-D-极简订单'
        verbose_name_plural = verbose_name
        db_table = 'crm_o_simpleorder'

    def __str__(self):
        return str(self.buyer_nick)

    def cs_info(self):
        cs_info = str(self.receiver_name) + "+" + str(self.receiver_area) + "+" + str(self.receiver_address) + "+" + str(self.receiver_mobile)
        return cs_info
    cs_info.short_description = '客户信息'