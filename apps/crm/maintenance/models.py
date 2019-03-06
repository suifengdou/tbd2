# -*- coding:  utf-8 -*-
# @Time    :  2018/11/26 13: 47
# @Author  :  Hann
# @Site    : 
# @File    :  urls.py.py
# @Software:  PyCharm


from django.db import models

from db.base_model import BaseModel


class MaintenanceInfo(BaseModel):
    ERP_FIELD = {
        '保修单号': 'maintenance_order_id',
        '保修单状态': 'order_status',
        '收发仓库': 'warehouse',
        '是否已处理过': 'null',
        '处理登记人': 'completer',
        '保修类型': 'maintenance_type',
        '故障类型': 'fault_type',
        '送修类型': 'transport_type',
        '序列号': 'machine_sn',
        '换新序列号': 'new_machine_sn',
        '发货订单编号': 'send_order_id',
        '保修结束语': 'appraisal',
        '关联订单号': 'null',
        '关联店铺': 'shop',
        '购买时间': 'purchase_time',
        '创建时间': 'ori_create_time',
        '创建人': 'ori_creator',
        '审核时间': 'handle_time',
        '审核人': 'handler_name',
        '保修完成时间': 'finish_time',
        '保修金额': 'fee',
        '保修数量': 'quantity',
        '完成人': 'null',
        '最后修改时间': 'last_handle_time',
        '外部推送编号': 'null',
        '推送错误信息': 'null',
        '客户网名': 'buyer_nick',
        '寄件客户姓名': 'sender_name',
        '寄件客户固话': 'null',
        '寄件客户手机': 'sender_mobile',
        '寄件客户邮编': 'null',
        '寄件客户省市县': 'sender_area',
        '寄件客户地址': 'sender_address',
        '收件物流公司': 'send_logistics_company',
        '收件物流单号': 'send_logistics_no',
        '收件备注': 'send_memory',
        '寄回客户姓名': 'return_name',
        '寄回客户固话': 'null',
        '寄回客户手机': 'return_mobile',
        '寄回邮编': 'null',
        '寄回省市区': 'return_area',
        '寄回地址': 'return_address',
        '寄件指定物流公司': 'return_logistics_company',
        '寄件物流单号': 'return_logistics_no',
        '寄件备注': 'return_memory',
        '保修货品商家编码': 'goods_id',
        '保修货品名称': 'goods_name',
        '保修货品简称': 'goods_abbreviation',
        '故障描述': 'description',
        '是否在保修期内': 'is_guarantee'
    }

    VERIFY_FIELD = ['maintenance_order_id', 'warehouse', 'completer', 'shop', 'ori_create_time', 'ori_creator',
                    'handle_time', 'finish_time', 'buyer_nick', 'sender_mobile', 'return_mobile',
                    'goods_id', 'goods_abbreviation', 'is_guarantee']

    ODER_STATUS = (
        (0, '未审核'),
        (1, '已处理'),
        (2, '无效'),
        (3, '异常'),
    )

    REPEAT_TAG_STATUS = (
        (0, '正常'),
        (1, '未处理'),
        (2, '产品'),
        (3, '维修'),
    )

    maintenance_order_id = models.CharField(max_length=50, verbose_name='保修单号')
    order_status = models.CharField(max_length=30, verbose_name='保修单状态')
    warehouse = models.CharField(max_length=50, verbose_name='收发仓库')
    completer = models.CharField(max_length=50, verbose_name='处理登记人')
    maintenance_type = models.CharField(max_length=50, verbose_name='保修类型')
    fault_type = models.CharField(max_length=50, verbose_name='故障类型')
    transport_type = models.CharField(max_length=50, verbose_name='送修类型')
    machine_sn = models.CharField(max_length=50, verbose_name='序列号')
    new_machine_sn = models.CharField(max_length=50, verbose_name='换新序列号')
    send_order_id = models.CharField(max_length=50, verbose_name='发货订单编号')
    appraisal = models.CharField(max_length=200, verbose_name='保修结束语')
    shop = models.CharField(max_length=60, verbose_name='关联店铺')
    purchase_time = models.DateTimeField(verbose_name='购买时间')
    ori_create_time = models.DateTimeField(null=True, blank=True, verbose_name='创建时间')
    ori_creator = models.CharField(null=True, blank=True, max_length=50, verbose_name='创建人')
    handle_time = models.DateTimeField(verbose_name='审核时间')
    handler_name = models.CharField(max_length=50, verbose_name='审核人')
    finish_time = models.DateTimeField(verbose_name='保修完成时间')
    fee = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='保修金额')
    quantity = models.IntegerField(verbose_name='保修数量')
    last_handle_time = models.DateTimeField(verbose_name='最后修改时间')
    buyer_nick = models.CharField(max_length=200, verbose_name='客户网名')
    sender_name = models.CharField(max_length=100, verbose_name='寄件客户姓名')
    sender_mobile = models.CharField(max_length=50, verbose_name='寄件客户手机')
    sender_area = models.CharField(max_length=50, verbose_name='寄件客户省市县')
    sender_address = models.CharField(max_length=200, verbose_name='寄件客户地址')
    send_logistics_company = models.CharField(max_length=50, verbose_name='收件物流公司')
    send_logistics_no = models.CharField(max_length=50, verbose_name='收件物流单号')
    send_memory = models.CharField(max_length=200, verbose_name='收件备注')
    return_name = models.CharField(max_length=50, verbose_name='寄回客户姓名')
    return_mobile = models.CharField(max_length=50, verbose_name='寄回客户手机')
    return_area = models.CharField(max_length=50, verbose_name='寄回省市区')
    return_address = models.CharField(max_length=200, verbose_name='寄回地址')
    return_logistics_company = models.CharField(max_length=50, verbose_name='寄件指定物流公司')
    return_logistics_no = models.CharField(max_length=50, verbose_name='寄件物流单号')
    return_memory = models.CharField(max_length=200, verbose_name='寄件备注')
    goods_id = models.CharField(max_length=60, verbose_name='保修货品商家编码')
    goods_name = models.CharField(max_length=150, verbose_name='保修货品名称')
    goods_abbreviation = models.CharField(max_length=60, verbose_name='保修货品简称')
    description = models.CharField(max_length=500, verbose_name='故障描述')
    is_guarantee = models.CharField(max_length=50, verbose_name='是否在保修期内')
    charge_status = models.CharField(default='', max_length=30, verbose_name='收费状态')
    charge_amount = models.IntegerField(default=0, verbose_name='收费金额')
    charge_memory = models.TextField(default='', verbose_name='收费说明')
    tocustomer_status = models.CharField(max_length=30, choices=ODER_STATUS, verbose_name='更新客户信息状态', default=0)
    towork_status = models.CharField(max_length=30, choices=ODER_STATUS, verbose_name='递交审核订单状态', default=0)

    class Meta:
        verbose_name = '保修单'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.maintenance_order_id

    @classmethod
    def verify_mandatory(cls, columns_key):
        for i in cls.VERIFY_FIELD:
            if i not in columns_key:
                return 'verify_field error, must have mandatory field: "{}""'.format(i)
        else:
            return None


class MaintenanceHandlingInfo(BaseModel):
    ODER_STATUS = (
        (0, '未审核'),
        (1, '已处理'),
        (2, '无效'),
        (3, '异常'),
    )

    REPEAT_TAG_STATUS = (
        (0, '正常'),
        (1, '未处理'),
        (2, '产品'),
        (3, '维修'),
        (4, '客服'),
    )

    maintenance_order_id = models.CharField(max_length=50, verbose_name='保修单号')
    warehouse = models.CharField(max_length=50, verbose_name='收发仓库')
    maintenance_type = models.CharField(max_length=50, verbose_name='保修类型')
    fault_type = models.CharField(max_length=50, verbose_name='故障类型')
    machine_sn = models.CharField(max_length=50, verbose_name='序列号')
    appraisal = models.CharField(max_length=200, verbose_name='保修结束语')
    shop = models.CharField(max_length=60, verbose_name='关联店铺')
    ori_create_time = models.DateTimeField(null=True, blank=True, verbose_name='创建时间')
    finish_time = models.DateTimeField(verbose_name='保修完成时间')
    buyer_nick = models.CharField(max_length=200, verbose_name='客户网名')
    sender_name = models.CharField(max_length=100, verbose_name='寄件客户姓名')
    sender_mobile = models.CharField(max_length=50, verbose_name='寄件客户手机')
    sender_area = models.CharField(max_length=50, verbose_name='寄件客户省市县')
    goods_name = models.CharField(max_length=150, verbose_name='保修货品名称')
    is_guarantee = models.CharField(max_length=50, verbose_name='是否在保')
    finish_date = models.DateField(verbose_name='保修完成日期')
    finish_month = models.DateField(verbose_name='保修完成月度')
    finish_year = models.DateField(verbose_name='保修完成年度')
    province = models.CharField(null=True, blank=True, max_length=50, verbose_name='省份')
    city = models.CharField(null=True, blank=True, max_length=50, verbose_name='城市')
    district = models.CharField(null=True, blank=True, max_length=50, verbose_name='区县')
    handling_status = models.CharField(max_length=30, choices=ODER_STATUS, verbose_name='操作状态', default=0)
    repeat_tag = models.CharField(max_length=30, choices=REPEAT_TAG_STATUS, verbose_name='重复维修标记', default=0)

    class Meta:
        verbose_name = '单据'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.maintenance_order_id


class MaintenanceSummary(BaseModel):
    finish_date = models.DateField(verbose_name='保修完成日期')
    order_count = models.IntegerField(default=0, verbose_name='完成保修数量')
    thirty_day_count = models.IntegerField(default=0, verbose_name='近三十天维修量')
    repeat_count = models.IntegerField(default=0, verbose_name='30天二次维修量')

    class Meta:
        verbose_name = '单据'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.finish_date











