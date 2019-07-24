# -*- coding:  utf-8 -*-
# @Time    :  2019/5/11 13: 47
# @Author  :  Hann
# @Site    :
# @File    :  models.py
# @Software:  PyCharm

from django.db import models
import django.utils.timezone as timezone
import pandas as pd

from db.base_model import BaseModel


class OriCallLogInfo(BaseModel):
    CALLLOG_DIC = {
        "时间": "call_time",
        "客户": "customer",
        "客户电话": "mobile",
        "公司": "company",
        "后续通话": "follow_up",
        "归属地": "location",
        "中继号": "relay_number",
        "客服": "customer_service",
        "通话类型": "call_category",
        "来源": "source",
        "任务": "task",
        "排队状态": "line_up_status",
        "DTMF": "dtmf",
        "排队耗时": "line_up_time",
        "设备状态": "device_status",
        "通话结果": "result",
        "外呼失败原因": "failure_reason",
        "通话录音": "call_recording",
        "通话时长": "call_length",
        "留言": "message",
        "响铃时间": "ring_time",
        "通话挂断方": "ring_off",
        "满意度评价": "degree_satisfaction",
        "外部电话": "outside_call",
        "主题": "Theme",
        "顺振": "sequence_ring",
        "相关客服": "relevant_cs",
        "生成工单": "work_order",
        "邮箱": "email",
        "标签": "tag",
        "描述": "description",
        "负责人": "leading_cadre",
        "负责组": "group",
        "等级": "degree",
        "是否在黑名单": "is_blacklist",
        "IVR录音": "ivr_record",
    }

    ORDERSTATUS = (
        (0, '已取消'),
        (1, '未处理'),
        (2, '已完成'),
    )

    call_time = models.DateTimeField(verbose_name='时间')
    customer = models.CharField(max_length=30, verbose_name='客户')
    mobile = models.CharField(max_length=30, verbose_name='客户电话')
    company = models.CharField(blank=True, null=True, max_length=30, verbose_name='公司')
    follow_up = models.CharField(blank=True, null=True, max_length=30, verbose_name='后续通话')
    location = models.CharField(blank=True, null=True, max_length=30, verbose_name='归属地')
    relay_number = models.CharField(max_length=30, verbose_name='中继号')
    customer_service = models.CharField(blank=True, null=True, max_length=30, verbose_name='客服')
    call_category = models.CharField(max_length=30, verbose_name='通话类型')
    source = models.CharField(max_length=30, verbose_name='来源')
    task = models.CharField(blank=True, null=True, max_length=30, verbose_name='任务')
    line_up_status = models.CharField(blank=True, null=True, max_length=30, verbose_name='排队状态')
    dtmf = models.CharField(blank=True, null=True, max_length=30, verbose_name='DTMF')
    line_up_time = models.TimeField(verbose_name='排队耗时')
    device_status = models.CharField(blank=True, null=True, max_length=30, verbose_name='设备状态')
    result = models.CharField(max_length=30, verbose_name='通话结果')
    failure_reason = models.CharField(blank=True, null=True, max_length=30, verbose_name='外呼失败原因')
    call_recording = models.TextField(blank=True, null=True, verbose_name='通话录音')
    call_length = models.TimeField(verbose_name='通话时长')
    message = models.TextField(verbose_name='留言')
    ring_time = models.TimeField(verbose_name='响铃时间')
    ring_off = models.CharField(blank=True, null=True, max_length=30, verbose_name='通话挂断方')
    degree_satisfaction = models.CharField(max_length=30, verbose_name='满意度评价')
    outside_call = models.CharField(blank=True, null=True, max_length=30, verbose_name='外部电话')
    Theme = models.CharField(blank=True, null=True, max_length=30, verbose_name='主题')
    sequence_ring = models.CharField(max_length=30, verbose_name='顺振')
    relevant_cs = models.IntegerField(blank=True, null=True, verbose_name='相关客服')
    work_order = models.CharField(blank=True, null=True, max_length=30, verbose_name='生成工单')
    email = models.CharField(max_length=60, verbose_name='邮箱')
    tag = models.CharField(blank=True, null=True, max_length=30, verbose_name='标签')
    description = models.CharField(blank=True, null=True, max_length=60, verbose_name='描述')
    leading_cadre = models.CharField(blank=True, null=True, max_length=30, verbose_name='负责人')
    group = models.CharField(blank=True, null=True, max_length=30, verbose_name='负责组')
    degree = models.CharField(max_length=30, verbose_name='等级')
    is_blacklist = models.CharField(max_length=30, verbose_name='是否在黑名单')
    ivr_record = models.CharField(blank=True, null=True, max_length=30, verbose_name='IVR录音')
    status = models.IntegerField(choices=ORDERSTATUS, default=1, verbose_name='单据状态')

    class Meta:
        verbose_name = '原始通话记录'
        verbose_name_plural = verbose_name
        db_table = 'crm_cal_oricalllog'

    def __str__(self):
        return self.mobile

