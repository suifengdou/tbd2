# -*- coding: utf-8 -*-
# @Time    : 2018/11/26 13:47
# @Author  : Hann
# @Site    :
# @File    : urls.py.py
# @Software: PyCharm


from django.db import models


from db.base_model import BaseModel


class RefundResource(BaseModel):
    VERIFY_FIELD = ['service_order_id', 'order_id', 'goods_id', 'goods_name', 'order_status', 'application_time',
                    'buyer_expectation', 'return_model', 'handler_name', 'express_id', 'express_company']
    ORDER_STATUS = (
        (0, '未审核'),
        (1, '已处理'),
        (2, '已完结'),
    )
    service_order_id = models.CharField(max_length=30, verbose_name=u'服务单号')
    order_id = models.CharField(max_length=30, verbose_name=u'订单号')
    goods_id = models.CharField(max_length=30, verbose_name=u'商品编号')
    goods_name = models.CharField(max_length=250, verbose_name=u'商品名称')
    goods_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='商品金额')
    order_status = models.CharField(null=True, blank=True, max_length=20, verbose_name=u'服务单状态')
    application_time = models.DateTimeField(null=True, blank=True, verbose_name='售后服务单申请时间')
    bs_initial_time = models.DateTimeField(null=True, blank=True, verbose_name=u'商家首次审核时间')
    bs_handle_time = models.DateTimeField(null=True, blank=True, verbose_name=u'商家首次处理时间')
    duration = models.IntegerField(null=True, blank=True, verbose_name=u'售后服务单整体时长')
    bs_result = models.CharField(null=True, blank=True, max_length=20, verbose_name=u'审核结果')
    bs_result_desc = models.CharField(null=True, blank=True, max_length=20, verbose_name=u'处理结果描述')
    buyer_expectation = models.CharField(max_length=20, verbose_name=u'客户预期处理方式')
    return_model = models.CharField(max_length=20, verbose_name=u'返回方式')
    buyer_problem_desc = models.CharField(null=True, blank=True, max_length=500, verbose_name=u'客户问题描述')
    last_handle_time = models.DateTimeField(null=True, blank=True, max_length=20, verbose_name=u'最新审核时间')
    handle_opinion = models.CharField(null=True, blank=True, max_length=250, verbose_name=u'审核意见')
    handler_name = models.CharField(max_length=20, verbose_name=u'审核人姓名')
    take_delivery_time = models.DateTimeField(null=True, blank=True, verbose_name=u'取件时间')
    take_delivery_status = models.CharField(null=True, blank=True, max_length=20, verbose_name=u'取件状态')
    delivery_time = models.CharField(null=True, blank=True, max_length=30, verbose_name=u'发货时间')
    express_id = models.CharField(max_length=30, verbose_name=u'运单号')
    express_fee = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2, verbose_name=u'运费金额')
    express_company = models.CharField(max_length=20, verbose_name=u'快递公司')
    receive_time = models.CharField(null=True, blank=True, max_length=50, verbose_name=u'商家收货时间')
    refund_reason = models.CharField(null=True, blank=True, max_length=50, verbose_name=u'收货登记原因')
    receiver = models.CharField(null=True, blank=True, max_length=20, verbose_name=u'收货人')
    completer = models.CharField(null=True, blank=True, max_length=20, verbose_name=u'处理人')
    refund_amount = models.CharField(null=True, blank=True, max_length=20, verbose_name=u'退款金额')
    renew_express_id = models.CharField(null=True, blank=True, max_length=30, verbose_name=u'换新订单')
    renew_goods_id = models.CharField(null=True, blank=True, max_length=20, verbose_name=u'换新商品编号')
    is_quick_refund = models.CharField(null=True, blank=True, max_length=10, verbose_name=u'是否闪退订单')
    handlingstatus = models.SmallIntegerField(choices=ORDER_STATUS, verbose_name='最终录入状态', default=0)

    class Meta:
        verbose_name = 'ASS-京东FBP退库单源数据'
        verbose_name_plural = verbose_name
        db_table = 'ass_jdfbp_refundresource'

    def __str__(self):
        return self.service_order_id

    @classmethod
    def verify_mandatory(cls, columns_key):
        for i in cls.VERIFY_FIELD:
            if i not in columns_key:
                return 'verify_field error, must have mandatory field: "{}""'.format(i)
        else:
            return None


class PendingRefundResource(RefundResource):
    class Meta:
        verbose_name = 'ASS-未建单退货单'
        verbose_name_plural = verbose_name
        proxy = True