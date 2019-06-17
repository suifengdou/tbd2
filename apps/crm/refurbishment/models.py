# -*- coding:  utf-8 -*-
# @Time    :  2019/5/11 13: 47
# @Author  :  Hann
# @Site    :
# @File    :  models.py
# @Software:  PyCharm

from django.db import models
import django.utils.timezone as timezone

from db.base_model import BaseModel
from apps.oms.machine.models import MachineInfo
from tbd2.settings import AUTH_USER_MODEL


class ApprasialInfo(BaseModel):
    appraisal = models.CharField(unique=True, max_length=30, verbose_name='故障判断')

    class Meta:
        verbose_name = '故障列表'
        verbose_name_plural = verbose_name
        db_table = 'crm_ref_appraisalinfo'
        index_together = [
            'appraisal',
        ]

    def __str__(self):
        return self.appraisal


class OriRefurbishInfo(BaseModel):
    ODER_STATUS = (
        (0, '未递交'),
        (1, '已处理'),
        (2, '重复订单'),
        (3, '异常'),
    )
    BATCH = (
        ("A", "A"),
        ("B", "B"),
        ("C", "C"),
        ("D", "D"),
    )
    ref_time = models.DateTimeField(default=timezone.now, verbose_name='翻新时间')
    goods_name = models.ForeignKey(MachineInfo, on_delete=models.CASCADE, verbose_name='机器名称')
    appraisal = models.ForeignKey(ApprasialInfo,  on_delete=models.CASCADE, default=39, verbose_name='故障判断')
    pre_sn = models.CharField(max_length=20, verbose_name="序列号前缀")
    mid_batch = models.CharField(default="A", choices=BATCH, max_length=1, verbose_name='中间批次识别')
    tail_sn = models.CharField(null=True, max_length=5, verbose_name='尾号')
    submit_tag = models.IntegerField(default=0, choices=ODER_STATUS, verbose_name='生成状态')
    new_sn = models.CharField(null=True, blank=True, max_length=30, verbose_name='新序列号')
    created_by = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='%(class)s_createdby', verbose_name='翻新人', null=True)

    class Meta:
        verbose_name = '原始翻新列表'
        verbose_name_plural = verbose_name
        db_table = 'crm_ref_orirefurbinshinfo'

    def __str__(self):
        return self.tail_sn


class PrivateOriRefurbishInfo(OriRefurbishInfo):
    class Meta:
        verbose_name = '私有翻新列表'
        verbose_name_plural = verbose_name
        proxy = True


class RefurbishInfo(BaseModel):
    ODER_STATUS = (
        (0, '未递交'),
        (1, '已处理'),
        (2, '售后质量'),
        (3, '异常'),
    )
    ref_time = models.DateTimeField(verbose_name='翻新时间')
    goods_name = models.CharField(max_length=60, verbose_name='机器名称')
    goods_id = models.CharField(max_length=30, verbose_name='机器编码')
    appraisal = models.CharField(max_length=60, verbose_name='故障判断')
    m_sn = models.CharField(max_length=30, verbose_name='机器序列号')
    technician = models.CharField(max_length=30, verbose_name='技术员')
    memo = models.CharField(null=True, blank=True, max_length=60, verbose_name='备注信息')
    submit_tag = models.IntegerField(default=0, choices=ODER_STATUS, verbose_name='递交状态')
    summary_tag = models.IntegerField(default=0, choices=ODER_STATUS, verbose_name='统计状态')

    class Meta:
        verbose_name = '翻新列表'
        verbose_name_plural = verbose_name
        db_table = 'crm_ref_refurbinshinfo'

    def __str__(self):
        return self.m_sn


class RefurbishTechSummary(BaseModel):
    statistical_time = models.DateTimeField(verbose_name='统计时间')
    technician = models.CharField(max_length=30, verbose_name='技术员')
    quantity = models.IntegerField(verbose_name='翻新数量')

    class Meta:
        verbose_name = '技术员翻新统计列表'
        verbose_name_plural = verbose_name
        db_table = 'crm_ref_refurbishtechsummary'

    def __str__(self):
        return self.statistical_time


class PrivateRefurbishTechSummary(RefurbishTechSummary):
    class Meta:
        verbose_name = '私有技术员翻新统计列表'
        verbose_name_plural = verbose_name
        proxy = True


class RefurbishGoodSummary(BaseModel):
    ODER_STATUS = (
        (0, '未递交'),
        (1, '已处理'),
        (2, '已出库'),
        (3, '异常'),
    )
    statistical_time = models.DateTimeField(verbose_name='统计时间')
    goods_name = models.CharField(max_length=60, verbose_name='机器名称')
    goods_id = models.CharField(max_length=30, verbose_name='机器编码')
    quantity = models.IntegerField(verbose_name='翻新数量')
    submit_tag = models.IntegerField(default=0, choices=ODER_STATUS, verbose_name='生成状态')

    class Meta:
        verbose_name = '翻新机器统计列表'
        verbose_name_plural = verbose_name
        db_table = 'crm_ref_refurbishgoodsummary'

    def __str__(self):
        return self.statistical_time


