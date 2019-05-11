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



class ApprasialInfo(BaseModel):
    appraisal = models.CharField(max_length=30, verbose_name='故障判断')

    class Meta:
        verbose_name = '故障列表'
        verbose_name_plural = verbose_name
        db_table = 'crm_ref_appraisalinfo'

    def __str__(self):
        return self.appraisal


class OirRefurbishInfo(BaseModel):
    ODER_STATUS = (
        (0, '未递交'),
        (1, '已处理'),
        (2, '无效'),
        (3, '异常'),
    )
    ref_time = models.DateTimeField(default=timezone.now, verbose_name='翻新时间')
    goods_name = models.ForeignKey(MachineInfo, on_delete=models.CASCADE, verbose_name='机器名称')
    appraisal = models.ForeignKey(ApprasialInfo, on_delete=models.CASCADE, verbose_name='故障判断')
    pre_sn = models.CharField(max_length=20, verbose_name="序列号前缀")
    mid_batch = models.CharField(default="A", max_length=1, verbose_name='中间批次识别')
    tail_sn = models.CharField(null=True, max_length=5, verbose_name='尾号')
    submit_tag = models.IntegerField(choices=ODER_STATUS, verbose_name='生成状态')

    class Meta:
        verbose_name = '原始翻新列表'
        verbose_name_plural = verbose_name
        db_table = 'crm_ref_orirefurbinshinfo'

    def __str__(self):
        return self.goods_name


class RefurbishInfo(BaseModel):
    ref_time = models.DateTimeField(default=timezone.now, verbose_name='翻新时间')
    goods_name = models.ForeignKey(MachineInfo, on_delete=models.CASCADE, verbose_name='机器名称')
    appraisal = models.ForeignKey(ApprasialInfo, on_delete=models.CASCADE, verbose_name='故障判断')
    m_sn = models.CharField(max_length=30, verbose_name='机器序列号')

    class Meta:
        verbose_name = '翻新列表'
        verbose_name_plural = verbose_name
        db_table = 'crm_ref_refurbinshinfo'

    def __str__(self):
        return self.m_sn





