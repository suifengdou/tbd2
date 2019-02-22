# -*- coding:  utf-8 -*-
# @Time    :  2018/11/26 13: 47
# @Author  :  Hann
# @Site    : 
# @File    :  urls.py.py
# @Software:  PyCharm


from django.db import models

from db.base_model import BaseModel


class OrderInfo(BaseModel):

    ERP_FIELD = {
        "订单编号": "erp_order_id",
        "店铺": "shop",
        "订单来源": "order_source",
        "仓库": "warehouse",
        "子单原始单号": "sub_original_order_id",
        "订单状态": "status",
        "订单类型": "order_type",
        "货到付款": "cash_on_delivery",
        "订单退款状态": "refund_status",
        "交易时间": "order_time",
        "付款时间": "pay_time",
        "客户网名": "buyer_nick",
        "收件人": "receiver_name",
        "收货地区": "receiver_area",
        "收货地址": "receiver_address",
        "收件人手机": "receiver_mobile",
        "分销商": "distributor",
        "来源组合装编号": "discreteness_source_id",
        "收件人电话": "receiver_telephone",
        "邮编": "zip_code",
        "区域": "order_area",
        "物流公司": "logistics_company",
        "物流单号": "invoice_no",
        "买家留言": "buyer_message",
        "客服备注": "seller_remark",
        "打印备注": "print_remark",
        "订单支付金额": "payment",
        "邮费": "post_fee",
        "订单总优惠": "discount_fee",
        "应收金额": "total_fee",
        "款到发货金额": "payment_and_delivery_fee",
        "货到付款金额": "cod_fee",
        "预估重量": "weight",
        "需要发票": "has_invoice",
        "发票抬头": "invoice_rise",
        "发票内容": "invoice_content",
        "业务员": "salesman",
        "审核人": "auditor",
        "商家编码": "goods_id",
        "货品编号": "goods_code",
        "货品名称": "goods_name",
        "规格名称": "goods_specification",
        "平台货品名称": "platform_goods_name",
        "平台规格名称": "platform_goods_specification",
        "下单数量": "quantity",
        "标价": "fixed",
        "货品总优惠": "goods_discount_fee",
        "成交价": "goods_price",
        "分摊后价格": "allocated_price",
        "打折比": "discount_ratio",
        "实发数量": "real_quantity",
        "分摊后总价": "allocated_total_fee",
        "退款前支付金额": "before_refund_payment",
        "分摊邮费": "allocated_post_fee",
        "单品支付金额": "goods_payment",
        "拆自组合装": "discreteness_id",
        "赠品方式": "gift_type"
    }

    VERIFY_FIELD = ["shop", "order_time", "pay_time", "receiver_name", "receiver_area", "receiver_address",
                    "receiver_mobile", "payment", "goods_id", "goods_name", "real_quantity", "goods_payment"]

    ODER_STATUS = (
        (0, '未审核'),
        (1, '已处理'),
        (2, '无效'),
        (3, '异常'),
    )

    erp_order_id = models.CharField(null=True, blank=True, max_length=30, verbose_name='订单编号')
    shop = models.CharField(max_length=30, verbose_name='店铺')
    order_source = models.CharField(null=True, blank=True, max_length=30, verbose_name='订单来源')
    warehouse = models.CharField(null=True, blank=True, max_length=30, verbose_name='仓库')
    sub_original_order_id = models.CharField(null=True, blank=True, max_length=30, db_index=True, verbose_name='子单原始单号')
    status = models.CharField(null=True, blank=True, max_length=30, verbose_name='订单状态')
    order_type = models.CharField(null=True, blank=True, max_length=30, verbose_name='订单类型')
    cash_on_delivery = models.CharField(null=True, blank=True, max_length=30, verbose_name='货到付款')
    refund_status = models.CharField(null=True, blank=True, max_length=30, verbose_name='订单退款状态')
    order_time = models.DateTimeField(verbose_name='交易时间')
    pay_time = models.DateTimeField(null=True, blank=True, verbose_name='付款时间')
    buyer_nick = models.CharField(null=True, blank=True, max_length=100, db_index=True, verbose_name='客户网名')
    receiver_name = models.CharField(max_length=100, verbose_name='收件人')
    receiver_area = models.CharField(null=True, blank=True, max_length=30, verbose_name='收货地区')
    receiver_address = models.CharField(max_length=200, verbose_name='收货地址')
    receiver_mobile = models.CharField(max_length=30, db_index=True, verbose_name='收件人手机')
    distributor = models.CharField(null=True, blank=True, max_length=30, verbose_name='分销商')
    discreteness_source_id = models.CharField(null=True, blank=True, max_length=30, verbose_name='来源组合装编号')
    receiver_telephone = models.CharField(null=True, blank=True, max_length=30, verbose_name='收件人电话')
    zip_code = models.CharField(null=True, blank=True, max_length=30, verbose_name='邮编')
    order_area = models.CharField(null=True, blank=True, max_length=30, verbose_name='区域')
    logistics_company = models.CharField(null=True, blank=True, max_length=30, verbose_name='物流公司')
    logistics_no = models.CharField(null=True, blank=True, max_length=30, verbose_name='物流单号')
    buyer_message = models.CharField(null=True, blank=True, max_length=800, verbose_name='买家留言')
    seller_remark = models.CharField(null=True, blank=True, max_length=800, verbose_name='客服备注')
    print_remark = models.CharField(null=True, blank=True, max_length=500, verbose_name='打印备注')
    payment = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='订单支付金额')
    post_fee = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2, verbose_name='邮费')
    discount_fee = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2, verbose_name='订单总优惠')
    total_fee = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2, verbose_name='应收金额')
    payment_and_delivery_fee = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2,
                                                   verbose_name='款到发货金额')
    cod_fee = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2, verbose_name='货到付款金额')
    weight = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2, verbose_name='预估重量')
    has_invoice = models.CharField(null=True, blank=True, max_length=30, verbose_name='需要发票')
    invoice_rise = models.CharField(null=True, blank=True, max_length=100, verbose_name='发票抬头')
    invoice_content = models.CharField(null=True, blank=True, max_length=100, verbose_name='发票内容')
    salesman = models.CharField(null=True, blank=True, max_length=30, verbose_name='业务员')
    auditor = models.CharField(null=True, blank=True, max_length=30, verbose_name='审核人')
    goods_id = models.CharField(max_length=30, verbose_name='商家编码')
    goods_code = models.CharField(null=True, blank=True, max_length=30, verbose_name='货品编号')
    goods_name = models.CharField(max_length=150, verbose_name='货品名称')
    goods_specification = models.CharField(null=True, blank=True, max_length=30, verbose_name='规格名称')
    platform_goods_name = models.CharField(null=True, blank=True, max_length=150, verbose_name='平台货品名称')
    platform_goods_specification = models.CharField(null=True, blank=True, max_length=150, verbose_name='平台规格名称')
    quantity = models.IntegerField(null=True, blank=True, verbose_name='下单数量')
    fixed = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2, verbose_name='标价')
    goods_discount_fee = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2,
                                             verbose_name='货品总优惠')
    goods_price = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2, verbose_name='成交价')
    allocated_price = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2, verbose_name='分摊后价格')
    discount_ratio = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2, verbose_name='打折比')
    real_quantity = models.IntegerField(verbose_name='实发数量')
    allocated_total_fee = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2,
                                              verbose_name='分摊后总价')
    before_refund_payment = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2,
                                                verbose_name='退款前支付金额')
    allocated_post_fee = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2,
                                             verbose_name='分摊邮费')
    goods_payment = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2, verbose_name='单品支付金额')
    discreteness_id = models.CharField(null=True, blank=True, max_length=30, verbose_name='拆自组合装')
    gift_type = models.CharField(null=True, blank=True, max_length=30, verbose_name='赠品方式')
    tocustomer_status = models.CharField(max_length=30, choices=ODER_STATUS, verbose_name='生成客户信息状态', default=0)
    totendency_ht_status = models.CharField(max_length=30, choices=ODER_STATUS, verbose_name='生成习惯时间状态', default=0)
    totendency_ha_status = models.CharField(max_length=30, choices=ODER_STATUS, verbose_name='生成习惯区域状态', default=0)
    totendency_ac_status = models.CharField(max_length=30, choices=ODER_STATUS, verbose_name='生成消费能力状态', default=0)
    platform = models.CharField(default='其他', max_length=30, verbose_name='平台')
    exception_tag = models.BooleanField(default=0, verbose_name='手机异常标记')

    class Meta:
        verbose_name = '订单'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.erp_order_id

    @classmethod
    def verify_mandatory(cls, columns_key):
        for i in cls.VERIFY_FIELD:
            if i not in columns_key:
                return 'verify_field error, must have mandatory field: "{}""'.format(i)
        else:
            return None
