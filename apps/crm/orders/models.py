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
        (1, '已导入过的订单'),
        (2, '待确认重复订单'),

    )
    PROCESS_TAG = (
        (0, '未处理'),
        (1, '待核实'),
        (2, '已确认'),
        (3, '待清理'),
        (4, '已处理'),
        (5, '驳回'),
        (6, '特殊订单'),
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
    src_tids = models.CharField(max_length=101, null=True, blank=True, db_index=True, verbose_name='原始子订单号')
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
        return str(self.id)

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
        (2, '未标记'),
        (3, '未财审'),
        (4, '已完成'),
    )
    MISTAKE_LIST = (
        (0, '正常'),
        (1, '已导入过的订单'),
        (2, 'UT中无此店铺'),
        (3, 'UT中店铺关联平台'),
        (4, '保存出错'),

    )
    PROCESS_TAG = (
        (0, '未处理'),
        (1, '待核实'),
        (2, '已确认'),
        (3, '待清理'),
        (4, '已处理'),
        (5, '驳回'),
        (6, '特殊订单'),
        (7, '手工设置成功'),
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
    ori_order = models.ForeignKey(OriOrderInfo, on_delete=models.CASCADE, verbose_name='原始订单')
    buyer_nick = models.CharField(max_length=150, db_index=True, verbose_name='客户网名')
    trade_no = models.CharField(max_length=120, db_index=True, verbose_name='订单编号')
    receiver_name = models.CharField(max_length=150, verbose_name='收件人')
    receiver_address = models.CharField(max_length=256, verbose_name='收货地址')
    receiver_mobile = models.CharField(max_length=40, db_index=True, verbose_name='收件人手机')
    pay_time = models.DateTimeField(verbose_name='付款时间')
    receiver_area = models.CharField(max_length=150, verbose_name='收货地区')
    logistics_no = models.CharField(null=True, blank=True, max_length=150, verbose_name='物流单号')
    buyer_message = models.TextField(null=True, blank=True, verbose_name='买家留言')
    cs_remark = models.TextField(null=True, blank=True, max_length=800, verbose_name='客服备注')
    src_tids = models.CharField(max_length=101, null=True, blank=True,  db_index=True,  verbose_name='原始子订单号')
    num = models.IntegerField(verbose_name='实发数量')
    price = models.FloatField(verbose_name='成交价')
    share_amount = models.FloatField(verbose_name='货品成交总价')
    goods_name = models.CharField(max_length=255, verbose_name='货品名称')
    spec_code = models.CharField(max_length=150, verbose_name='商家编码', db_index=True)
    shop_name = models.CharField(max_length=128, db_index=True, verbose_name='店铺')
    logistics_name = models.CharField(null=True, blank=True, max_length=60, verbose_name='物流公司')
    warehouse_name = models.CharField(max_length=100, db_index=True, verbose_name='仓库')
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
        return str(self.id)

    @classmethod
    def verify_mandatory(cls, columns_key):
        for i in cls.VERIFY_FIELD:
            if i not in columns_key:
                return 'verify_field error, must have mandatory field: "{}""'.format(i)
        else:
            return None

    def cs_info(self):
        cs_info = str(self.receiver_name) + "+" + str(self.receiver_area) + "+" + str(self.receiver_address) + "+" + str(self.receiver_mobile)
        return cs_info
    cs_info.short_description = '客户信息'


class SimpleOrder(OrderInfo):
    class Meta:
        verbose_name = 'CRM-UT订单-极简订单'
        verbose_name_plural = verbose_name
        proxy = True


class SubmitOrder(OrderInfo):
    class Meta:
        verbose_name = 'CRM-UT订单-未处理'

        verbose_name_plural = verbose_name
        proxy = True


class CheckOrder(OrderInfo):
    class Meta:
        verbose_name = 'CRM-UT订单-未关联'
        verbose_name_plural = verbose_name
        proxy = True


class PartWHCheckOrder(OrderInfo):
    class Meta:
        verbose_name = 'CRM-UT订单-未关联配件仓'
        verbose_name_plural = verbose_name
        proxy = True


class PartWHOrder(OrderInfo):
    class Meta:
        verbose_name = 'CRM-UT订单-配件仓查询'
        verbose_name_plural = verbose_name
        proxy = True


class MachineWHCheckOrder(OrderInfo):
    class Meta:
        verbose_name = 'CRM-UT订单-未关联整机仓'
        verbose_name_plural = verbose_name
        proxy = True


class MachineWHOrder(OrderInfo):
    class Meta:
        verbose_name = 'CRM-UT订单-整机仓查询'
        verbose_name_plural = verbose_name
        proxy = True


class CenterTWHCheckOrder(OrderInfo):
    class Meta:
        verbose_name = 'CRM-UT订单-未关联中央仓'
        verbose_name_plural = verbose_name
        proxy = True


class CenterTWHOrder(OrderInfo):
    class Meta:
        verbose_name = 'CRM-UT订单-中央仓查询'
        verbose_name_plural = verbose_name
        proxy = True


class LabelOptions(OrderInfo):
    class Meta:
        verbose_name = 'CRM-UT订单-未标记'
        verbose_name_plural = verbose_name
        proxy = True


class TailShopOrder(OrderInfo):
    class Meta:
        verbose_name = 'CRM-UT订单-尾货配件查询'
        verbose_name_plural = verbose_name
        proxy = True


class OriOrderList(BaseModel):
    ORDERSTATUS = (
        (0, '已取消'),
        (1, '未处理'),
        (2, '已完成'),
    )

    ori_order = models.OneToOneField(OriOrderInfo, on_delete=models.CASCADE, related_name='listori', verbose_name='原始订单')
    order_status = models.SmallIntegerField(choices=ORDERSTATUS, default=1, db_index=True, verbose_name='单据状态')

    class Meta:
        verbose_name = 'CRM-原始订单-递交列表'
        verbose_name_plural = verbose_name
        db_table = 'crm_o_oriorderlist'

    def __str__(self):
        return str(self.ori_order)




class OriBMSOrderInfo(BaseModel):

    VERIFY_FIELD = ['trade_no', 'shop_name', 'warehouse_name', 'buyer_nick',
                    'receiver_name', 'province', 'city', 'district', 'street', 'receiver_address',
                    'receiver_mobile', 'goods_name', 'spec_code', 'ori_order_status', 'goods_weight',
                    'num', 'price', 'share_amount', 'pay_time', 'logistics_name', 'logistics_no',
                    'cs_remark', 'src_tids']

    ORDERSTATUS = (
        (0, '已取消'),
        (1, '未处理'),
        (2, '已完成'),
    )
    MISTAKE_LIST = (
        (0, '正常'),
        (1, '已导入过的订单'),
        (2, '待确认重复订单'),

    )
    PROCESS_TAG = (
        (0, '未处理'),
        (1, '待核实'),
        (2, '已确认'),
        (3, '待清理'),
        (4, '已处理'),
        (5, '驳回'),
        (6, '特殊订单'),
    )

    buyer_nick = models.CharField(max_length=150, db_index=True, verbose_name='买家昵称')
    trade_no = models.CharField(max_length=60, db_index=True, verbose_name='订单编号')
    receiver_name = models.CharField(max_length=150, verbose_name='收货人姓名')
    receiver_address = models.CharField(max_length=256, verbose_name='收货人地址')
    province = models.CharField(max_length=40, verbose_name='省')
    city = models.CharField(max_length=40, verbose_name='市')
    district = models.CharField(max_length=40, verbose_name='区')
    street = models.CharField(max_length=40, verbose_name='街道')
    receiver_mobile = models.CharField(max_length=40, db_index=True, verbose_name='手机')
    pay_time = models.DateTimeField(verbose_name='支付时间')
    logistics_no = models.CharField(null=True, blank=True, max_length=150, verbose_name='运单号')
    cs_remark = models.TextField(null=True, blank=True, max_length=800, verbose_name='卖家备注')
    src_tids = models.CharField(max_length=120, db_index=True,  verbose_name='交易订单号')
    num = models.IntegerField(verbose_name='订货数量')
    price = models.FloatField(verbose_name='订单金额')
    share_amount = models.FloatField(verbose_name='商品小计')
    goods_name = models.CharField(max_length=255, verbose_name='商品名称')
    spec_code = models.CharField(max_length=150, verbose_name='商品编码', db_index=True)
    shop_name = models.CharField(max_length=128, verbose_name='店铺名称')
    logistics_name = models.CharField(null=True, blank=True, max_length=60, verbose_name='快递公司')
    warehouse_name = models.CharField(max_length=100, verbose_name='仓库名称')
    order_category = models.CharField(max_length=40, db_index=True,  verbose_name='订单类型')
    ori_order_status = models.CharField(max_length=40, verbose_name='状态')
    goods_weight = models.CharField(max_length=40, verbose_name='商品重量(克)')

    order_status = models.SmallIntegerField(choices=ORDERSTATUS, default=1, db_index=True, verbose_name='单据状态')
    process_tag = models.SmallIntegerField(choices=PROCESS_TAG, default=0, verbose_name='处理标签')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误列表')

    class Meta:
        verbose_name = 'CRM-原始BMS订单-查询'
        verbose_name_plural = verbose_name
        db_table = 'crm_o_bms_oriorderinfo'

    def __str__(self):
        return str(self.id)

    @classmethod
    def verify_mandatory(cls, columns_key):
        for i in cls.VERIFY_FIELD:
            if i not in columns_key:
                return 'verify_field error, must have mandatory field: "{}""'.format(i)
        else:
            return None


class SubmitOBMSOrder(OriBMSOrderInfo):
    class Meta:
        verbose_name = 'CRM-原始BMS订单-未提交'
        verbose_name_plural = verbose_name
        proxy = True
