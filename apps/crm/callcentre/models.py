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

    ORDERSTATUS = (
        (0, '已取消'),
        (1, '未处理'),
        (2, '未抽检'),
        (3, '已完成'),
    )
    PROCESS_TAG = (
        (0, '未处理'),
        (1, '待核实'),
        (2, '已确认'),
        (3, '待清账'),
        (4, '已处理'),
        (5, '特殊订单'),
    )
    MISTAKE_LIST = (
        (0, '正常'),
        (1, '重复建单'),
        (2, '无补寄原因'),
        (3, '无店铺'),
        (4, '补寄配件记录格式错误'),
        (5, '补寄原因错误'),
        (6, '单据创建失败'),
    )
    LOGICAL_DECISION = (
        (0, '否'),
        (1, '是'),
    )
    CATEGORY = (
        (0, '常规'),
        (1, '订单'),
    )

    call_time = models.DateTimeField(verbose_name='时间')
    mobile = models.CharField(max_length=30, verbose_name='客户电话')
    location = models.CharField(blank=True, null=True, max_length=30, verbose_name='归属地')
    relay_number = models.CharField(max_length=30, verbose_name='中继号')
    customer_service = models.CharField(blank=True, null=True, max_length=30, verbose_name='客服')
    call_category = models.CharField(max_length=30, verbose_name='通话类型')
    source = models.CharField(max_length=30, verbose_name='来源')
    line_up_status = models.CharField(blank=True, null=True, max_length=30, verbose_name='排队状态')
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
    theme = models.CharField(blank=True, null=True, max_length=230, verbose_name='主题')
    sequence_ring = models.CharField(max_length=30, verbose_name='顺振')
    relevant_cs = models.CharField(blank=True, null=True, max_length=30, verbose_name='相关客服')
    work_order = models.CharField(blank=True, null=True, max_length=30, verbose_name='生成工单')
    email = models.CharField(blank=True, null=True, max_length=60, verbose_name='邮箱')
    tag = models.CharField(blank=True, null=True, max_length=30, verbose_name='标签')
    description = models.TextField(blank=True, null=True, verbose_name='描述')
    leading_cadre = models.CharField(blank=True, null=True, max_length=30, verbose_name='负责人')
    group = models.CharField(blank=True, null=True, max_length=30, verbose_name='负责组')
    degree = models.CharField(max_length=30, verbose_name='等级')
    is_blacklist = models.CharField(max_length=30, verbose_name='是否在黑名单')
    call_id = models.CharField(max_length=230, verbose_name='call_id')

    reason = models.CharField(blank=True, null=True, max_length=60, verbose_name='补寄原因')
    call_class = models.CharField(blank=True, null=True, max_length=60, verbose_name='来电类别')
    goods_name = models.CharField(blank=True, null=True, max_length=60, verbose_name='商品型号')
    process_category = models.CharField(blank=True, null=True, max_length=60, verbose_name='处理方式')
    goods_id = models.CharField(blank=True, null=True, max_length=60, verbose_name='产品编号')
    purchase_time = models.CharField(blank=True, null=True, max_length=60, verbose_name='购买日期')
    service_info = models.CharField(blank=True, null=True, max_length=230, verbose_name='补寄配件记录')
    shop = models.CharField(blank=True, null=True, max_length=60, verbose_name='店铺')

    order_status = models.IntegerField(choices=ORDERSTATUS, default=1, verbose_name='单据状态')
    process_tag = models.IntegerField(choices=PROCESS_TAG, default=0, verbose_name='处理标签')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误列表')
    is_sampling = models.SmallIntegerField(choices=LOGICAL_DECISION, default=0, verbose_name='是否抽检')
    content_category = models.SmallIntegerField(choices=CATEGORY, default=0, verbose_name='内容类型')

    class Meta:
        verbose_name = 'CRM-原始通话记录-查询'
        verbose_name_plural = verbose_name
        db_table = 'crm_cal_oricalllog'

    def __str__(self):
        return self.mobile

    @classmethod
    def verify_mandatory(cls, columns_key):
        VERIFY_FIELD = ['call_time', 'mobile', 'location', 'relay_number', 'customer_service', 'call_category',
                        'source', 'line_up_status', 'line_up_time', 'device_status', 'result', 'failure_reason',
                        'call_recording', 'call_length', 'message', 'ring_time', 'ring_off', 'degree_satisfaction',
                        'theme', 'sequence_ring', 'relevant_cs', 'work_order', 'email', 'tag', 'description',
                        'leading_cadre', 'group', 'degree', 'is_blacklist', 'call_id', 'reason', 'call_class',
                        'goods_name', 'process_category', 'goods_id', 'purchase_time']

        for i in VERIFY_FIELD:
            if i not in columns_key:
                return 'verify_field error, must have mandatory field: "{}""'.format(i)
        else:
            return None

    def recorder(self):
        if self.call_recording:
            from django.utils.safestring import mark_safe
            return mark_safe('<a href="%s" target="_blank">录音</a>' % self.call_recording)
        else:
            return "无"
    recorder.short_description = '对话录音'


class CheckOriCall(OriCallLogInfo):
    class Meta:
        verbose_name = 'CRM-原始通话记录-未处理'
        verbose_name_plural = verbose_name
        proxy = True
