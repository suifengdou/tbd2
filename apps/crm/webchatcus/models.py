# -*- coding:  utf-8 -*-
# @Time    :  2018/12/11 13: 47
# @Author  :  Hann
# @Site    : 
# @File    :  urls.py.py
# @Software:  PyCharm


from django.db import models

from db.base_model import BaseModel
from apps.crm.customers.models import CustomerInfo



class OriWebchatInfo(BaseModel):

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

    type = models.CharField(max_length=60, verbose_name='机器类别')
    goods_code = models.CharField(max_length=60, verbose_name='产品ID')
    goods_name = models.CharField(max_length=150, verbose_name='产品名称')
    goods_series = models.CharField(max_length=60, verbose_name='货品序号')
    goods_id = models.CharField(max_length=150, verbose_name='型号')
    produce_year = models.CharField(null=True, blank=True,  max_length=60, verbose_name='生产年')
    produce_week = models.CharField(null=True, blank=True, max_length=60, verbose_name='生产周')
    produce_batch = models.CharField(null=True, blank=True, max_length=60, verbose_name='周批次')
    produce_sn = models.CharField(null=True, blank=True, max_length=150, verbose_name='码值')
    activity_time = models.DateTimeField(verbose_name='激活时间')
    purchase_time = models.DateTimeField(verbose_name='购买日期')
    grade = models.CharField(max_length=10, verbose_name='评价星级（1-5）')
    comment = models.TextField(null=True, blank=True, verbose_name='评论内容')
    register_time = models.DateTimeField(verbose_name='产品注册时间')
    cs_id = models.CharField(max_length=60, verbose_name='用户id')
    nick_name = models.CharField(null=True, blank=True, max_length=230, verbose_name='昵称')
    area = models.CharField(null=True, blank=True, max_length=150, verbose_name='所在地区')
    gender = models.CharField(max_length=10, verbose_name='性别')
    check_status = models.CharField(max_length=60, verbose_name='审核状态')
    name = models.CharField(null=True, blank=True, max_length=150, verbose_name='真实姓名')
    cs_gender = models.CharField(null=True, blank=True, max_length=10, verbose_name='真实性别')
    cs_mobile = models.CharField(null=True, blank=True, max_length=60, verbose_name='真实手机号')
    cs_area = models.CharField(null=True, blank=True, max_length=150, verbose_name='真实区域')
    cs_address = models.CharField(null=True, blank=True, max_length=230, verbose_name='真实地址')
    living_area = models.CharField(null=True, blank=True, max_length=60, verbose_name='家庭面积')
    family = models.CharField(null=True, blank=True, max_length=150, verbose_name='家庭成员')
    habit = models.CharField(null=True, blank=True, max_length=150,  verbose_name='兴趣爱好')
    other_habit = models.CharField(null=True, blank=True, max_length=150, verbose_name='其他兴趣')
    auth_time = models.DateTimeField(verbose_name='授权时间')

    order_status = models.SmallIntegerField(choices=ORDERSTATUS, default=1, db_index=True, verbose_name='单据状态')
    process_tag = models.SmallIntegerField(choices=PROCESS_TAG, default=0, verbose_name='处理标签')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误列表')

    class Meta:
        verbose_name = 'crm-微信公众号原始单据-查询'
        verbose_name_plural = verbose_name
        db_table = 'crm_webchart_oriorderinfo'

    def __str__(self):
        return str(self.id)


# 单据导入
class OWOrder(OriWebchatInfo):

    VERIFY_FIELD = ['type', 'goods_code', 'goods_name', 'goods_series', 'goods_id', 'produce_year', 'produce_week',
                    'produce_batch', 'produce_sn', 'activity_time', 'purchase_time', 'grade',
                    'comment', 'register_time', 'cs_id', 'nick_name', 'area', 'gender', 'check_status', 'name',
                    'cs_gender', 'cs_mobile', 'cs_area', 'cs_address', 'living_area', 'family', 'habit',
                    'other_habit', 'auth_time']

    class Meta:
        verbose_name = 'crm-微信公众号原始单据-未递交'
        verbose_name_plural = verbose_name
        proxy = True

    @classmethod
    def verify_mandatory(cls, columns_key):
        for i in cls.VERIFY_FIELD:
            if i not in columns_key:
                return 'verify_field error, must have mandatory field: "{}""'.format(i)
        else:
            return None


class WebchatCus(BaseModel):

    ORDERSTATUS = (
        (0, '已取消'),
        (1, '未处理'),
        (2, '已完成'),
    )

    customer = models.OneToOneField(CustomerInfo, on_delete=models.CASCADE, verbose_name='客户')
    order_status = models.SmallIntegerField(choices=ORDERSTATUS, default=1, db_index=True, verbose_name='单据状态')

    class Meta:
        verbose_name = 'crm-微信公众号客户列表-查询'
        verbose_name_plural = verbose_name
        db_table = 'crm_webchart_customers'

    def __str__(self):
        return str(self.customer)


class WebchatInfo(BaseModel):

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
    customer = models.ForeignKey(CustomerInfo, on_delete=models.CASCADE, verbose_name='客户')

    type = models.CharField(max_length=60, verbose_name='机器类别')
    goods_name = models.CharField(max_length=150, verbose_name='产品名称')
    goods_series = models.CharField(max_length=60, verbose_name='货品序号')
    goods_id = models.CharField(max_length=150, verbose_name='型号')
    produce_sn = models.CharField(max_length=150, verbose_name='码值')
    activity_time = models.DateTimeField(verbose_name='激活时间')
    purchase_time = models.DateTimeField(verbose_name='购买日期')
    comment = models.TextField(null=True, blank=True, verbose_name='评论内容')
    register_time = models.DateTimeField(verbose_name='产品注册时间')
    cs_id = models.CharField(max_length=60, verbose_name='用户id')
    nick_name = models.CharField(null=True, blank=True, max_length=230, verbose_name='昵称')
    area = models.CharField(null=True, blank=True, max_length=150, verbose_name='所在地区')
    gender = models.CharField(max_length=10, verbose_name='性别')
    name = models.CharField(null=True, blank=True, max_length=150, verbose_name='真实姓名')
    cs_gender = models.CharField(null=True, blank=True, max_length=10, verbose_name='真实性别')
    cs_area = models.CharField(null=True, blank=True, max_length=150, verbose_name='真实区域')
    cs_address = models.CharField(null=True, blank=True, max_length=230, verbose_name='真实地址')
    living_area = models.CharField(null=True, blank=True, max_length=60, verbose_name='家庭面积')
    family = models.CharField(null=True, blank=True, max_length=150, verbose_name='家庭成员')
    habit = models.CharField(null=True, blank=True, max_length=150,  verbose_name='兴趣爱好')
    other_habit = models.CharField(null=True, blank=True, max_length=150, verbose_name='其他兴趣')

    order_status = models.SmallIntegerField(choices=ORDERSTATUS, default=1, db_index=True, verbose_name='单据状态')
    process_tag = models.SmallIntegerField(choices=PROCESS_TAG, default=0, verbose_name='处理标签')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误列表')

    class Meta:
        verbose_name = 'CRM-微信公众号单据-查询'
        verbose_name_plural = verbose_name
        db_table = 'crm_webchart_orderinfo'

    def __str__(self):
        return str(self.customer)


class WOrder(WebchatInfo):
    class Meta:
        verbose_name = 'crm-微信公众号单据-未递交'
        verbose_name_plural = verbose_name
        proxy = True


# 微信公众号原始延保码
class OriWarrantyInfo(BaseModel):

    ORDERSTATUS = (
        (0, '已取消'),
        (1, '未处理'),
        (2, '已完成'),
    )
    MISTAKE_LIST = (
        (0, '正常'),
        (1, '已导入过的订单'),
        (2, '还未生成客户档案'),

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
    warranty_sn = models.CharField(unique=True, max_length=150, verbose_name='延保码')
    batch_name = models.CharField(max_length=150, verbose_name='所属批次')
    duration = models.IntegerField(verbose_name='延保时长')
    goods_name = models.CharField(max_length=150, verbose_name='商品型号')
    produce_sn = models.CharField(max_length=150, verbose_name='序列号')
    purchase_time = models.DateTimeField(verbose_name='购买时间')
    register_time = models.DateTimeField(null=True, blank=True, verbose_name='产品注册时间')
    webchat_name = models.CharField(null=True, blank=True, max_length=150, verbose_name='微信昵称')
    name = models.CharField(null=True, blank=True, max_length=150, verbose_name='姓名')
    gender = models.CharField(max_length=10, verbose_name='性别')

    smartphone = models.CharField(null=True, blank=True, max_length=60, verbose_name='手机号')
    area = models.CharField(null=True, blank=True, max_length=150, verbose_name='真实区域')
    living_area = models.CharField(null=True, blank=True, max_length=60, verbose_name='家庭面积')
    family = models.CharField(null=True, blank=True, max_length=150, verbose_name='家庭成员')
    habit = models.CharField(null=True, blank=True, max_length=150,  verbose_name='兴趣爱好')
    other_habit = models.CharField(null=True, blank=True, max_length=150, verbose_name='其他兴趣')

    order_status = models.SmallIntegerField(choices=ORDERSTATUS, default=1, db_index=True, verbose_name='单据状态')
    process_tag = models.SmallIntegerField(choices=PROCESS_TAG, default=0, verbose_name='处理标签')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误列表')

    class Meta:
        verbose_name = 'crm-微信公众号原始延保码-查询'
        verbose_name_plural = verbose_name
        db_table = 'crm_webchart_oriwarranty'


# 单据导入
class OWNumber(OriWarrantyInfo):

    VERIFY_FIELD = ['warranty_sn', 'batch_name', 'duration', 'goods_name', 'produce_sn',
                    'purchase_time', 'register_time', 'webchat_name', 'name', 'birthday', 'gender',
                    'smartphone', 'area', 'living_area', 'family', 'habit', 'other_habit']

    class Meta:
        verbose_name = 'crm-微信公众号原始延保码-未递交'
        verbose_name_plural = verbose_name
        proxy = True

    @classmethod
    def verify_mandatory(cls, columns_key):
        for i in cls.VERIFY_FIELD:
            if i not in columns_key:
                return 'verify_field error, must have mandatory field: "{}""'.format(i)
        else:
            return None


class WarrantyInfo(BaseModel):

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
    customer = models.ForeignKey(CustomerInfo, on_delete=models.CASCADE, verbose_name='客户')

    warranty_sn = models.CharField(unique=True, max_length=150, verbose_name='延保码')
    batch_name = models.CharField(max_length=150, verbose_name='所属批次')
    duration = models.IntegerField(verbose_name='延保时长')
    goods_name = models.CharField(max_length=150, verbose_name='商品型号')
    produce_sn = models.CharField(max_length=150, verbose_name='序列号')
    purchase_time = models.DateTimeField(verbose_name='购买时间')
    register_time = models.DateTimeField(null=True, blank=True, verbose_name='产品注册时间')
    webchat_name = models.CharField(null=True, blank=True, max_length=150, verbose_name='微信昵称')
    name = models.CharField(null=True, blank=True, max_length=150, verbose_name='姓名')
    birthday = models.DateTimeField(null=True, blank=True, verbose_name='生日')
    gender = models.CharField(max_length=10, verbose_name='性别')

    area = models.CharField(null=True, blank=True, max_length=150, verbose_name='真实区域')
    living_area = models.CharField(null=True, blank=True, max_length=60, verbose_name='家庭面积')
    family = models.CharField(null=True, blank=True, max_length=150, verbose_name='家庭成员')
    habit = models.CharField(null=True, blank=True, max_length=150,  verbose_name='兴趣爱好')
    other_habit = models.CharField(null=True, blank=True, max_length=150, verbose_name='其他兴趣')

    order_status = models.SmallIntegerField(choices=ORDERSTATUS, default=1, db_index=True, verbose_name='单据状态')
    process_tag = models.SmallIntegerField(choices=PROCESS_TAG, default=0, verbose_name='处理标签')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误列表')

    class Meta:
        verbose_name = 'crm-微信公众号延保码-查询'
        verbose_name_plural = verbose_name
        db_table = 'crm_webchart_warranty'


# 单据导入
class WNumber(WarrantyInfo):

    class Meta:
        verbose_name = 'crm-微信公众号延保码-未递交'
        verbose_name_plural = verbose_name
        proxy = True

