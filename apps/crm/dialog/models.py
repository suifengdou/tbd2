# -*- coding:  utf-8 -*-
# @Time    :  2020/04/24 13: 47
# @Author  :  Hann
# @Site    : 
# @File    :  urls.py.py
# @Software:  PyCharm


from django.db import models

from db.base_model import BaseModel
from apps.users.models import UserProfile


class ServicerInfo(BaseModel):
    CATEGORY = (
        (0, '机器人'),
        (1, '人工'),
    )
    name = models.CharField(max_length=150, verbose_name='昵称')
    platform = models.CharField(max_length=60, verbose_name='平台')
    username = models.ForeignKey(UserProfile, on_delete=models.CASCADE, blank=True, null=True, verbose_name='人名')
    category = models.SmallIntegerField(choices=CATEGORY, default=1, verbose_name='客服类型')

    class Meta:
        verbose_name = 'CRM-对话-客服网名'
        verbose_name_plural = verbose_name
        db_table = 'crm_dialog_servicer'

    def __str__(self):
        return self.name


class SensitiveInfo(BaseModel):
    ORDER_STATUS = (
        (0, '被取消'),
        (1, '正常'),
    )
    CATEGORY = (
        (0, '负向'),
        (1, '正面'),
    )
    words = models.CharField(max_length=10, unique=True, verbose_name='敏感字')
    index_num = models.IntegerField(verbose_name='指数')
    category = models.SmallIntegerField(choices=CATEGORY, default=0, verbose_name='敏感字类型')
    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='单据状态')

    class Meta:
        verbose_name = 'CRM-对话-敏感字'
        verbose_name_plural = verbose_name
        db_table = 'crm_dialog_sensitive'

    def __str__(self):
        return self.words

    @classmethod
    def verify_mandatory(cls, columns_key):
        VERIFY_FIELD = ['words', 'index']

        for i in VERIFY_FIELD:
            if i not in columns_key:
                return 'verify_field error, must have mandatory field: "{}""'.format(i)
        else:
            return None


class DialogTag(BaseModel):
    ORDER_STATUS = (
        (0, '被取消'),
        (1, '正常'),
    )

    CATEGORY = (
        (0, '无法定义'),
        (1, '售前'),
        (2, '售后'),
    )
    name = models.CharField(max_length=30, verbose_name='标签名')
    category = models.SmallIntegerField(choices=CATEGORY, default=0, verbose_name='标签类型')
    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='单据状态')

    class Meta:
        verbose_name = 'CRM-对话-标签'
        verbose_name_plural = verbose_name
        db_table = 'crm_dialog_tag'

    def __str__(self):
        return self.name


class OriDialogTB(BaseModel):
    ORDER_STATUS = (
        (0, '被取消'),
        (1, '正常'),
    )
    shop = models.CharField(max_length=60, verbose_name='店铺', db_index=True)
    customer = models.CharField(max_length=150, verbose_name='客户', db_index=True)
    start_time = models.DateTimeField(verbose_name='开始时间')
    end_time = models.DateTimeField(verbose_name='结束时间')
    min = models.IntegerField(verbose_name='总人次')
    dialog_tag = models.ForeignKey(DialogTag, on_delete=models.CASCADE, null=True, blank=True, verbose_name='对话标签')
    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='单据状态', db_index=True)

    class Meta:
        verbose_name = 'CRM-淘系对话客户-查询'
        unique_together = ('shop', 'customer')
        verbose_name_plural = verbose_name
        db_table = 'crm_dialog_oritaobao'

    def __str__(self):
        return self.customer


class OriDetailTB(BaseModel):
    ORDER_STATUS = (
        (0, '被取消'),
        (1, '正常'),
    )

    STATUS = (
        (0, '客服'),
        (1, '顾客'),
    )
    LOGICAL_DECISION = (
        (0, '否'),
        (1, '是'),
    )
    MISTAKE_LIST = (
        (0, '正常'),
        (1, '对话格式错误'),
        (2, '重复导入'),
        (3, '差价货品名称错误'),
        (4, '差价金额填写错误'),
        (5, '差价收款人姓名错误'),
        (6, '差价支付宝名称错误'),
        (7, '差价订单号错误'),
        (8, '差价核算公式格式错误'),
        (9, '差价核算公式计算错误'),
        (10, '差价核算结果与上报差价不等'),
        (11, '差价类型只能是1或者3'),
    )
    CATEGORY = (
        (0, '常规'),
        (1, '订单'),
        (2, '差价'),
    )

    dialog_tb = models.ForeignKey(OriDialogTB, on_delete=models.CASCADE, verbose_name='对话')
    sayer = models.CharField(max_length=150, verbose_name='讲话者', db_index=True)
    d_status = models.SmallIntegerField(choices=STATUS, verbose_name='角色')
    time = models.DateTimeField(verbose_name='时间', db_index=True)
    interval = models.IntegerField(verbose_name='对话间隔(秒)')
    content = models.TextField(verbose_name='内容')

    index_num = models.IntegerField(default=0, verbose_name='对话负面指数')

    category = models.SmallIntegerField(choices=CATEGORY, default=0, verbose_name='内容类型')
    extract_tag = models.SmallIntegerField(choices=LOGICAL_DECISION, default=0, verbose_name='是否提取订单', db_index=True)
    sensitive_tag = models.SmallIntegerField(choices=LOGICAL_DECISION, default=0, verbose_name='是否过滤')
    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='单据状态', db_index=True)
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误列表')

    class Meta:
        verbose_name = 'CRM-淘系对话信息-查询'
        verbose_name_plural = verbose_name
        db_table = 'crm_diadetail_oritaobao'

    def __str__(self):
        return self.sayer


class CheckODTB(OriDetailTB):
    class Meta:
        verbose_name = 'CRM-淘宝对话信息-未过滤'
        verbose_name_plural = verbose_name
        proxy = True


class ExtractODTB(OriDetailTB):
    class Meta:
        verbose_name = 'CRM-淘宝对话信息-未提取'
        verbose_name_plural = verbose_name
        proxy = True


class MyExtractODTB(OriDetailTB):
    class Meta:
        verbose_name = 'CRM-淘宝对话信息-未提取个人'
        verbose_name_plural = verbose_name
        proxy = True


class ExceptionODTB(OriDetailTB):
    class Meta:
        verbose_name = 'CRM-淘宝对话信息-敏感对话'
        verbose_name_plural = verbose_name
        proxy = True


class OriDialogJD(BaseModel):
    ORDER_STATUS = (
        (0, '被取消'),
        (1, '正常'),
    )
    CATEGORY = (
        (0, '自动'),
        (1, '人工'),
    )
    shop = models.CharField(max_length=60, verbose_name='店铺', db_index=True)
    customer = models.CharField(max_length=150, verbose_name='客户', db_index=True)
    start_time = models.DateTimeField(verbose_name='开始时间')
    end_time = models.DateTimeField(verbose_name='结束时间')
    min = models.IntegerField(verbose_name='总人次')
    category = models.SmallIntegerField(choices=CATEGORY, default=1, verbose_name='对话类型')
    dialog_tag = models.ForeignKey(DialogTag, on_delete=models.CASCADE, null=True, blank=True, verbose_name='对话标签')
    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='单据状态', db_index=True)

    class Meta:
        verbose_name = 'CRM-京东对话客户-查询'
        unique_together = ('shop', 'customer')
        verbose_name_plural = verbose_name
        db_table = 'crm_dialog_orijingdong'

    def __str__(self):
        return self.customer


class OriDetailJD(BaseModel):
    ORDER_STATUS = (
        (0, '被取消'),
        (1, '未过滤'),
        (2, '未质检'),
    )

    STATUS = (
        (0, '客服'),
        (1, '顾客'),
    )
    LOGICAL_DECISION = (
        (0, '否'),
        (1, '是'),
    )
    MISTAKE_LIST = (
        (0, '正常'),
        (1, '对话格式错误'),
        (2, '重复导入'),
    )
    CATEGORY = (
        (0, '常规'),
        (1, '订单'),
    )

    dialog_jd = models.ForeignKey(OriDialogJD, on_delete=models.CASCADE, verbose_name='对话')
    sayer = models.CharField(max_length=150, verbose_name='讲话者', db_index=True)
    d_status = models.SmallIntegerField(choices=STATUS, verbose_name='角色')
    time = models.DateTimeField(verbose_name='时间', db_index=True)
    interval = models.IntegerField(verbose_name='对话间隔(秒)')
    content = models.TextField(verbose_name='内容')

    index_num = models.IntegerField(default=0, verbose_name='对话负面指数')

    category = models.SmallIntegerField(choices=CATEGORY, default=0, verbose_name='内容类型')

    extract_tag = models.SmallIntegerField(choices=LOGICAL_DECISION, default=0, verbose_name='是否提取订单', db_index=True)
    sensitive_tag = models.SmallIntegerField(choices=LOGICAL_DECISION, default=0, verbose_name='是否过滤')
    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='单据状态', db_index=True)
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误列表')

    class Meta:
        verbose_name = 'CRM-京东对话信息-查询'
        verbose_name_plural = verbose_name
        db_table = 'crm_diadetail_orijingdong'

    def __str__(self):
        return self.sayer


class CheckODJD(OriDetailJD):
    class Meta:
        verbose_name = 'CRM-京东对话信息-未过滤'
        verbose_name_plural = verbose_name
        proxy = True


class ExtractODJD(OriDetailJD):
    class Meta:
        verbose_name = 'CRM-京东对话信息-未提取'
        verbose_name_plural = verbose_name
        proxy = True


class ExceptionODJD(OriDetailJD):
    class Meta:
        verbose_name = 'CRM-京东对话信息-敏感对话'
        verbose_name_plural = verbose_name
        proxy = True


class OriDialogOW(BaseModel):
    ORDER_STATUS = (
        (0, '被取消'),
        (1, '正常'),
    )
    shop = models.CharField(max_length=60, verbose_name='店铺', db_index=True)
    customer = models.CharField(max_length=150, verbose_name='客户', db_index=True)
    start_time = models.DateTimeField(verbose_name='开始时间')
    end_time = models.DateTimeField(verbose_name='结束时间')
    min = models.IntegerField(verbose_name='总人次')
    dialog_tag = models.ForeignKey(DialogTag, on_delete=models.CASCADE, null=True, blank=True, verbose_name='对话标签')
    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='单据状态', db_index=True)

    class Meta:
        verbose_name = 'CRM-官网对话客户-查询'
        unique_together = ('shop', 'customer')
        verbose_name_plural = verbose_name
        db_table = 'crm_dialog_oriofficial'

    def __str__(self):
        return self.customer

    @classmethod
    def verify_mandatory(cls, columns_key):
        VERIFY_FIELD = ['customer', 'start_time', 'content', 'dialog_id']

        for i in VERIFY_FIELD:
            if i not in columns_key:
                return 'verify_field error, must have mandatory field: "{}""'.format(i)
        else:
            return None


class OriDetailOW(BaseModel):
    ORDER_STATUS = (
        (0, '被取消'),
        (1, '正常'),
    )

    STATUS = (
        (0, '客服'),
        (1, '顾客'),
    )
    LOGICAL_DECISION = (
        (0, '否'),
        (1, '是'),
    )
    MISTAKE_LIST = (
        (0, '正常'),
        (1, '对话格式错误'),
        (2, '重复导入'),
    )
    CATEGORY = (
        (0, '常规'),
        (1, '订单'),
    )

    dialog_ow = models.ForeignKey(OriDialogOW, on_delete=models.CASCADE, verbose_name='对话')
    sayer = models.CharField(max_length=150, verbose_name='讲话者', db_index=True)
    d_status = models.SmallIntegerField(choices=STATUS, verbose_name='角色')
    time = models.DateTimeField(verbose_name='时间', db_index=True)
    interval = models.IntegerField(verbose_name='对话间隔(秒)')
    content = models.TextField(verbose_name='内容')

    index_num = models.IntegerField(default=0, verbose_name='对话负面指数')

    category = models.SmallIntegerField(choices=CATEGORY, default=0, verbose_name='内容类型')
    extract_tag = models.SmallIntegerField(choices=LOGICAL_DECISION, default=0, verbose_name='是否提取订单', db_index=True)
    sensitive_tag = models.SmallIntegerField(choices=LOGICAL_DECISION, default=0, verbose_name='是否过滤')
    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='单据状态', db_index=True)
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误列表')

    class Meta:
        verbose_name = 'CRM-官网对话信息-查询'
        verbose_name_plural = verbose_name
        db_table = 'crm_diadetail_oriofficial'

    def __str__(self):
        return self.sayer


class CheckODOW(OriDetailOW):
    class Meta:
        verbose_name = 'CRM-官网对话信息-未过滤'
        verbose_name_plural = verbose_name
        proxy = True


class ExtractODOW(OriDetailOW):
    class Meta:
        verbose_name = 'CRM-官网对话信息-未提取'
        verbose_name_plural = verbose_name
        proxy = True


class MyExtractODOW(OriDetailOW):
    class Meta:
        verbose_name = 'CRM-官网对话信息-未提取个人'
        verbose_name_plural = verbose_name
        proxy = True


class ExceptionODOW(OriDetailOW):
    class Meta:
        verbose_name = 'CRM-官网对话信息-敏感对话'
        verbose_name_plural = verbose_name
        proxy = True


class DOWID(BaseModel):
    dialog_id = models.CharField(unique=True, max_length=30, verbose_name='对话ID')

    class Meta:
        verbose_name = 'CRM-官网对话信息-对话ID'
        verbose_name_plural = verbose_name
        db_table = 'crm_diadetail_dowid'

    def __str__(self):
        return self.dialog_id