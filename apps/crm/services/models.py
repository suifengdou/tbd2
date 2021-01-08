# -*- coding:  utf-8 -*-
# @Time    :  2020/11/19 13: 47
# @Author  :  Hann
# @Site    : 
# @File    :  urls.py.py
# @Software:  PyCharm


from django.db import models

from db.base_model import BaseModel
from apps.crm.customers.models import CustomerInfo


class ServicesInfo(BaseModel):
    ORDERSTATUS = (
        (0, '已取消'),
        (1, '待生成'),
        (2, '待执行'),
        (3, '待分配'),
        (4, '待完成'),
        (5, '已完成'),
    )
    ORDER_CATEGORY = (
        (1, "电话"),
        (2, "短信"),
        (3, "旺旺留言"),
    )
    ORDER_TYPE = (
        (1, "常规任务"),
        (2, "快捷注册任务"),
    )
    MISTAKE_LIST = (
        (0, '正常'),
        (1, '任务说明和要点为必填项'),
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
    )
    name = models.CharField(max_length=120, verbose_name='任务名称', unique=True, db_index=True)
    order_type = models.SmallIntegerField(choices=ORDER_TYPE, default=1, verbose_name='任务类型')
    order_category = models.SmallIntegerField(choices=ORDER_CATEGORY, default=1, db_index=True, verbose_name='任务执行类型')
    prepare_time = models.DateTimeField(blank=True, null=True, verbose_name='预计开始时间')
    start_time = models.DateTimeField(blank=True, null=True, verbose_name='实际开始时间')
    finish_time = models.DateTimeField(blank=True, null=True, verbose_name='完成时间')
    services_info = models.TextField(blank=True, null=True, verbose_name='任务说明和要点')
    quantity = models.IntegerField(verbose_name='任务客户数量')
    memorandum = models.CharField(blank=True, null=True, max_length=150, verbose_name='备注')
    order_status = models.SmallIntegerField(choices=ORDERSTATUS, default=1, db_index=True, verbose_name='单据状态')
    process_tag = models.SmallIntegerField(choices=PROCESS_TAG, default=0, verbose_name='处理标签')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误列表')
    count_down = models.IntegerField(blank=True, null=True, verbose_name='预计开始倒计时')
    received_num = models.IntegerField(default=0, verbose_name='待反馈数量')
    completed_num = models.IntegerField(default=0, verbose_name='已完成数量')

    class Meta:
        verbose_name = 'crm-关系任务-查询'
        verbose_name_plural = verbose_name
        db_table = 'crm_ser_orderinfo'

    def __str__(self):
        return str(self.name)

    def unhandle_num(self):
        unhandle_num = self.quantity - self.received_num - self.completed_num
        return unhandle_num
    unhandle_num.short_description = '未完成数量'


class SSICreate(ServicesInfo):

    class Meta:

        verbose_name = 'crm-关系任务-待生成'
        verbose_name_plural = verbose_name
        proxy = True


class SSIProcess(ServicesInfo):
    class Meta:
        verbose_name = 'crm-关系任务-待分配'
        verbose_name_plural = verbose_name
        proxy = True


class SSIDistribute(ServicesInfo):
    class Meta:
        verbose_name = 'crm-关系任务-可分配'
        verbose_name_plural = verbose_name
        proxy = True


class SSIFinished(ServicesInfo):
    class Meta:
        verbose_name = 'crm-关系任务-待完结'
        verbose_name_plural = verbose_name
        proxy = True


class ServicesDetail(BaseModel):

    ORDERSTATUS = (
        (0, '已取消'),
        (1, '待生成'),
        (2, '待分配'),
        (3, '待执行'),
        (4, '待反馈'),
        (5, '已完成'),
    )
    ORDER_OUTCOME = (
        (0, '未执行'),
        (1, "电话连通"),
        (2, "电话未通"),
        (3, "短信已发"),
        (4, "旺旺已留言"),
        (5, "旺旺留言失败"),
        (6, "客户自行注册"),
    )
    MISTAKE_LIST = (
        (0, '正常'),
        (1, '无实施时间'),
        (2, '无处理结果'),
        (3, '非旺旺任务无法批量完结'),
    )
    ORDER_TYPE = (
        (1, "常规任务"),
        (2, "快捷注册任务"),
    )
    PROCESS_TAG = (
        (0, '未处理'),
        (1, '待分配'),
        (2, '已领取'),
        (3, '待清理'),
        (4, '已处理'),
        (5, '驳回'),
        (6, '特殊订单'),
        (7, '自动过滤'),
    )
    customer = models.ForeignKey(CustomerInfo, on_delete=models.CASCADE, verbose_name='客户')
    services = models.ForeignKey(ServicesInfo, on_delete=models.CASCADE, verbose_name='关系任务')
    order_type = models.SmallIntegerField(choices=ORDER_TYPE, default=1, verbose_name='任务类型')
    target = models.CharField(max_length=150, verbose_name='任务对象')
    is_completed = models.BooleanField(default=False, verbose_name='目标是否达成')
    outcome = models.SmallIntegerField(default=0, choices=ORDER_OUTCOME, verbose_name='结果')
    handler = models.CharField(blank=True, null=True, max_length=60, verbose_name='实施人')
    handle_time = models.DateTimeField(blank=True, null=True, verbose_name='实施时间')
    memorandum = models.TextField(blank=True, null=True, max_length=220, verbose_name='备注')
    warranty_sn = models.CharField(blank=True, null=True, max_length=150, verbose_name='延保码')
    order_status = models.SmallIntegerField(choices=ORDERSTATUS, default=1, db_index=True, verbose_name='单据状态')
    process_tag = models.SmallIntegerField(choices=PROCESS_TAG, default=0, verbose_name='处理标签')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误列表')
    services_info = models.TextField(blank=True, null=True, verbose_name='任务说明和要点')

    class Meta:
        verbose_name = 'crm-关系任务明细-查询'
        verbose_name_plural = verbose_name
        db_table = 'crm_ser_orderdetail'

    def __str__(self):
        return str(self.customer)


class SDCreate(ServicesDetail):

    class Meta:
        verbose_name = 'crm-关系任务明细-待生成'
        verbose_name_plural = verbose_name
        proxy = True

    VERIFY_FIELD = ['services', 'warranty_sn', 'target']

    @classmethod
    def verify_mandatory(cls, columns_key):
        for i in cls.VERIFY_FIELD:
            if i not in columns_key:
                return 'verify_field error, must have mandatory field: "{}""'.format(i)
        else:
            return None


class SDDistribute(ServicesDetail):
    class Meta:
        verbose_name = 'crm-关系任务明细-待分配'
        verbose_name_plural = verbose_name
        proxy = True


class SDProcess(ServicesDetail):
    class Meta:
        verbose_name = 'crm-关系任务明细-待执行'
        verbose_name_plural = verbose_name
        proxy = True


class SDFeedback(ServicesDetail):
    class Meta:
        verbose_name = 'crm-关系任务明细-待反馈'
        verbose_name_plural = verbose_name
        proxy = True