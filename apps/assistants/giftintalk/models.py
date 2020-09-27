# -*- coding: utf-8 -*-
# @Time    : 2018/11/26 13:47
# @Author  : Hann
# @Site    :
# @File    : urls.py.py
# @Software: PyCharm

from django.db import models
import django.utils.timezone as timezone

from db.base_model import BaseModel
from apps.crm.dialog.models import OriDetailJD, OriDetailTB, OriDetailOW
from apps.crm.callcentre.models import OriCallLogInfo


class GiftInTalkInfo(BaseModel):
    ORDERSTATUS = (
        (0, '已取消'),
        (1, '未处理'),
        (2, '已完成'),
    )
    MISTAKE_LIST = (
        (0, '货品名称错误'),
        (1, '14天内重复订单'),
        (2, '14天外重复订单'),
        (3, '收货人，电话，地址不全'),
        (4, '地址中，二级市出错，请使用标准系统信息'),
        (5, '网名错误'),
        (6, '系统出错，请重复提交，无法解决时联系管理员'),
        (7, '平台出错'),
        (8, '同名订单'),
        (9, '手机错误'),
        (10, '集运仓地址'),

    )
    PLATFORM = (
        (0, '无'),
        (1, '淘系'),
        (2, '京东'),
        (3, '官方商城'),
        (4, '呼叫中心'),
    )
    ORDER_CATEGORY = (
        (1, '质量问题'),
        (2, '开箱即损'),
        (3, '礼品赠品'),
    )
    PROCESS_TAG = (
        (0, '未处理'),
        (1, '待核实'),
        (2, '已确认'),
        (3, '待清账'),
        (4, '已处理'),
        (5, '特殊订单'),
    )

    cs_information = models.CharField(max_length=300, verbose_name='收件信息')
    goods = models.CharField(max_length=250, verbose_name='赠品信息')
    servicer = models.CharField(max_length=50, verbose_name='客服')
    nickname = models.CharField(max_length=50, verbose_name='用户网名', db_index=True)
    order_id = models.CharField(max_length=50, null=True, blank=True, verbose_name='订单号')
    mistakes = models.IntegerField(choices=MISTAKE_LIST, null=True, blank=True, verbose_name='错误信息')
    order_status = models.IntegerField(choices=ORDERSTATUS, default=1, verbose_name='赠品单状态')
    platform = models.SmallIntegerField(choices=PLATFORM, default=0, verbose_name='平台')
    submit_user = models.CharField(null=True, blank=True, max_length=50, verbose_name='操作人')
    order_category = models.SmallIntegerField(choices=ORDER_CATEGORY, default=3, verbose_name='单据类型')
    shop = models.CharField(max_length=150, null=True, blank=True, verbose_name='店铺')
    process_tag = models.SmallIntegerField(choices=PROCESS_TAG, default=0, verbose_name='处理标签')

    class Meta:
        verbose_name = 'ASS-GT-手工订单提取查询'
        verbose_name_plural = verbose_name
        db_table = 'ass_gt_oriorder'


class GiftInTalkPendding(GiftInTalkInfo):

    class Meta:
        verbose_name = 'ASS-GT-手工订单提取递交'
        verbose_name_plural = verbose_name
        proxy = True


class GiftOrderInfo(BaseModel):
    ORDERSTATUS = (
        (0, '已取消'),
        (1, '未处理'),
        (2, '已完成'),
    )

    ORDER_CATEGORY = (
        (1, '质量问题'),
        (2, '开箱即损'),
        (3, '礼品赠品'),
    )

    shop = models.CharField(max_length=60, verbose_name='店铺名称')
    nickname = models.CharField(max_length=50, verbose_name='网名')
    receiver = models.CharField(max_length=50, verbose_name='收件人')
    address = models.CharField(max_length=250, verbose_name='地址')
    mobile = models.CharField(max_length=50, verbose_name='手机')

    d_condition = models.CharField(max_length=20, default="款到发货", verbose_name='发货条件')
    discount = models.SmallIntegerField(default=0, verbose_name='优惠金额')
    post_fee = models.SmallIntegerField(default=0, verbose_name='邮费')
    receivable = models.SmallIntegerField(default=0, verbose_name='应收合计')
    goods_price = models.SmallIntegerField(default=0, verbose_name='货品价格')
    total_prices = models.SmallIntegerField(default=0, verbose_name='货品总价')

    goods_id = models.CharField(max_length=50, verbose_name='商家编码')
    goods_name = models.CharField(max_length=50, verbose_name='货品名称')
    quantity = models.SmallIntegerField(verbose_name='货品数量')

    category = models.CharField(max_length=20, default="线下零售", verbose_name='订单类别')
    buyer_remark = models.CharField(max_length=300, default="线下零售", verbose_name='买家备注')
    cs_memoranda = models.CharField(null=True, blank=True, max_length=300, default="线下零售", verbose_name='客服备注')

    province = models.CharField(max_length=50, verbose_name='省')
    city = models.CharField(max_length=50, verbose_name='市')
    district = models.CharField(null=True, blank=True, max_length=50, verbose_name='区')

    order_id = models.CharField(null=True, blank=True, max_length=50, verbose_name='订单号')
    order_status = models.IntegerField(choices=ORDERSTATUS, default=1, verbose_name='赠品单状态')
    submit_user = models.CharField(null=True, blank=True, max_length=50, verbose_name='处理人')
    order_category = models.SmallIntegerField(choices=ORDER_CATEGORY, default=3, verbose_name='单据类型')

    class Meta:
        verbose_name = 'ASS-GT-手工预订单查询'
        verbose_name_plural = verbose_name
        db_table = 'ass_gt_order'

    def __str__(self):
        return self.order_id


class GiftOrderPendding(GiftOrderInfo):

    class Meta:
        verbose_name = 'ASS-GT-手工预订单处理'
        verbose_name_plural = verbose_name
        proxy = True


class GiftImportInfo(BaseModel):
    ORDERSTATUS = (
        (0, '已取消'),
        (1, '未处理'),
        (2, '已完成'),
    )

    shop = models.CharField(max_length=60, verbose_name='店铺名称')
    nickname = models.CharField(max_length=50, verbose_name='网名')
    receiver = models.CharField(max_length=50, verbose_name='收件人')
    address = models.CharField(max_length=250, verbose_name='地址')
    mobile = models.CharField(max_length=50, verbose_name='手机')

    d_condition = models.CharField(max_length=20, default="款到发货", verbose_name='发货条件')
    discount = models.SmallIntegerField(default=0, verbose_name='优惠金额')
    post_fee = models.SmallIntegerField(default=0, verbose_name='邮费')
    receivable = models.SmallIntegerField(default=0, verbose_name='应收合计')
    goods_price = models.SmallIntegerField(default=0, verbose_name='货品价格')
    total_prices = models.SmallIntegerField(default=0, verbose_name='货品总价')

    goods_id = models.CharField(max_length=50, verbose_name='商家编码')
    goods_name = models.CharField(max_length=50, verbose_name='货品名称')
    quantity = models.SmallIntegerField(verbose_name='货品数量')

    category = models.CharField(max_length=20, default="线下零售", verbose_name='订单类别')
    buyer_remark = models.CharField(max_length=300, verbose_name='买家备注')
    cs_memoranda = models.CharField(max_length=300, verbose_name='客服备注')

    province = models.CharField(max_length=50, verbose_name='省')
    city = models.CharField(max_length=50, verbose_name='市')
    district = models.CharField(null=True, blank=True, max_length=50, verbose_name='区')

    order_id = models.CharField(null=True, blank=True, max_length=50, verbose_name='订单号')
    order_status = models.IntegerField(choices=ORDERSTATUS, default=1, verbose_name='赠品单状态')
    submit_user = models.CharField(null=True, blank=True, max_length=50, verbose_name='处理人')
    erp_order_id = models.CharField(null=True, blank=True, unique=True, max_length=50, verbose_name='原始单号')

    class Meta:
        verbose_name = 'ASS-GT-手工ERP导入单据查询'
        verbose_name_plural = verbose_name
        db_table = 'ass_gt_erpimport'

    def __str__(self):
        return self.order_id


class GiftImportPendding(GiftImportInfo):
    class Meta:
        verbose_name = 'ASS-GT-手工ERP导入单据'
        verbose_name_plural = verbose_name
        proxy = True

    def __str__(self):
        return self.order_id


class OrderTBList(BaseModel):
    gift_order = models.OneToOneField(GiftInTalkInfo, on_delete=models.CASCADE, related_name='gift_tb', verbose_name='提取单据')
    talk_tb = models.OneToOneField(OriDetailTB, on_delete=models.CASCADE, verbose_name='淘宝对话')

    class Meta:
        verbose_name = '淘宝订单来源'
        verbose_name_plural = verbose_name
        db_table = 'ass_gt_order_tb'


class OrderJDList(BaseModel):
    gift_order = models.OneToOneField(GiftInTalkInfo, on_delete=models.CASCADE, related_name='gift_jd', verbose_name='提取单据')
    talk_jd = models.OneToOneField(OriDetailJD, on_delete=models.CASCADE, verbose_name='京东对话')

    class Meta:
        verbose_name = '京东订单来源'
        verbose_name_plural = verbose_name
        db_table = 'ass_gt_order_jd'


class OrderOWList(BaseModel):
    gift_order = models.OneToOneField(GiftInTalkInfo, on_delete=models.CASCADE, related_name='gift_ow', verbose_name='提取单据')
    talk_ow = models.OneToOneField(OriDetailOW, on_delete=models.CASCADE, verbose_name='官方商城对话')

    class Meta:
        verbose_name = '官方商城订单来源'
        verbose_name_plural = verbose_name
        db_table = 'ass_gt_order_ow'


class OrderCallList(BaseModel):
    gift_order = models.OneToOneField(GiftInTalkInfo, on_delete=models.CASCADE, related_name='gift_call', verbose_name='提取单据')
    call_order = models.OneToOneField(OriCallLogInfo, on_delete=models.CASCADE, verbose_name='400电话')

    class Meta:
        verbose_name = '呼叫中心来源'
        verbose_name_plural = verbose_name
        db_table = 'ass_gt_order_call'