# -*- coding: utf-8 -*-
# @Time    : 2020/2/5 9:27
# @Author  : Hann
# @Site    :
# @File    : models.py
# @Software: PyCharm

from django.db import models
import django.utils.timezone as timezone

from db.base_model import BaseModel


class WorkOrder(BaseModel):

    ORDER_STATUS = (
        (0, '已被取消'),
        (1, '未递交'),
        (2, '工单在理'),
        (3, '终审未理'),
        (4, '工单完结'),
    )

    CATEGORY = (
        (0, '产品'),
        (1, '业务'),
        (2, '权限'),
        (3, '其他'),
    )

    EMERGENCY = (
        (0, '常规'),
        (1, '紧急'),
        (2, '要命'),
    )

    LOGICAL_DEXISION = (
        (0, '否'),
        (1, '是'),
    )
    PROCESSTAG = (
        (0, '未分类'),
        (1, '待核实'),
        (2, '待审批'),
        (3, '已解决'),

    )
    MISTAKE_LIST = (
        (0, '正常'),
        (1, '反馈信息为空'),
        (2, '驳回'),
        (3, '没有确认解决'),
        (4, '平台错误')
    )

    PLATFORM = (
        (0, '无'),
        (1, '淘系'),
        (2, '非淘'),
    )

    information = models.TextField(max_length=600, verbose_name='初始问题信息')
    submit_time = models.DateTimeField(null=True, blank=True, verbose_name='客服提交时间')
    servicer = models.CharField(null=True, blank=True, max_length=60, verbose_name='客服')
    services_interval = models.IntegerField(null=True, blank=True, verbose_name='客服处理间隔(分钟)')
    servicer_feedback = models.TextField(null=True, blank=True, verbose_name='客服反馈')

    handler = models.CharField(null=True, blank=True, max_length=30, verbose_name='组长处理人')
    handle_time = models.DateTimeField(null=True, blank=True, verbose_name='组长处理时间')
    process_interval = models.IntegerField(null=True, blank=True, verbose_name='组长处理间隔(分钟)')
    feedback = models.TextField(null=True, blank=True, max_length=900, verbose_name='反馈内容')

    memo = models.TextField(null=True, blank=True, verbose_name='备注')

    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='工单状态')
    category = models.SmallIntegerField(choices=CATEGORY, verbose_name='工单类型')
    process_tag = models.SmallIntegerField(choices=PROCESSTAG, default=0, verbose_name='处理标签')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='异常原因')
    emergency_tag = models.SmallIntegerField(choices=EMERGENCY, default=0, verbose_name='紧急程度')
    platform = models.SmallIntegerField(choices=PLATFORM, default=0, verbose_name='平台')

    class Meta:
        verbose_name = 'EXT-求助工单-查询'
        verbose_name_plural = verbose_name
        db_table = 'ext_workorderemergency_order'

    def __str__(self):
        return str(self.id)


class WOCreate(WorkOrder):
    class Meta:
        verbose_name = 'EXT-求助工单-创建'
        verbose_name_plural = verbose_name
        proxy = True

    def __str__(self):
        return str(self.id)


class WOCheck(WorkOrder):
    class Meta:
        verbose_name = 'EXT-求助工单-审核'
        verbose_name_plural = verbose_name
        proxy = True

    def __str__(self):
        return str(self.id)


class WOFinish(WorkOrder):
    class Meta:
        verbose_name = 'EXT-求助工单-终审'
        verbose_name_plural = verbose_name
        proxy = True

    def __str__(self):
        return str(self.id)