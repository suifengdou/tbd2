# -*- coding: utf-8 -*-
# @Time    : 2019/4/9 20:58
# @Author  : Hann
# @Site    :
# @File    : models.py
# @Software: PyCharm


from django.db import models


from db.base_model import BaseModel
from apps.utils.geography.models import NationalityInfo


# Create your models here.
class MachineOrder(BaseModel):
    VERIFY_FIELD = ['identification', 'mfd', 'goods_id', 'manufactory', 'order_id', 'quantity', 'msn_segment']
    ODER_STATUS = (
        (0, '未递交'),
        (1, '已处理'),
        (2, '无效'),
        (3, '异常'),
    )
    identification = models.IntegerField(unique=True,verbose_name="订单序号")
    mfd = models.DateTimeField(verbose_name='要求交期')
    goods_id = models.CharField(max_length=30, verbose_name='型号')
    manufactory = models.CharField(max_length=50, verbose_name='工厂')
    order_id = models.CharField(max_length=50, verbose_name='生产单号')
    quantity = models.IntegerField(verbose_name='生产数量')
    msn_segment = models.CharField(max_length=150, verbose_name='序列号段')
    tosn_status = models.SmallIntegerField(default=0, choices=ODER_STATUS, verbose_name='sn列表生成状态')

    class Meta:
        verbose_name = '生产订单列表'
        verbose_name_plural = verbose_name
        db_table = 'oms_m_machineorder'

    def __str__(self):
        return self.order_id

    @classmethod
    def verify_mandatory(cls, columns_key):
        for i in cls.VERIFY_FIELD:
            if i not in columns_key:
                return 'verify_field error, must have mandatory field: "{}""'.format(i)
        else:
            return None


class MachineSN(BaseModel):
    ODER_STATUS = (
        (0, '未递交'),
        (1, '已处理'),
        (2, '无效'),
        (3, '异常'),
    )
    VERIFY_FIELD = ['mfd', 'm_sn', 'batch_number', 'manufactory', 'goods_id']
    mfd = models.DateTimeField(verbose_name='要求交期')
    m_sn = models.CharField(max_length=50, verbose_name='机器序列号')
    batch_number = models.CharField(max_length=50, verbose_name='批次号')
    manufactory = models.CharField(max_length=50, verbose_name='工厂')
    goods_id = models.CharField(max_length=30, verbose_name='型号')

    class Meta:
        verbose_name = '机器序列号列表'
        verbose_name_plural = verbose_name
        db_table = 'oms_m_machinsn'

    def __str__(self):
        return self.m_sn

    @classmethod
    def verify_mandatory(cls, columns_key):
        for i in cls.VERIFY_FIELD:
            if i not in columns_key:
                return 'verify_field error, must have mandatory field: "{}""'.format(i)
        else:
            return None


class FaultMachineSN(BaseModel):
    mfd = models.DateTimeField(verbose_name='生产日期')
    finish_time = models.DateTimeField(verbose_name='保修完成时间')
    m_sn = models.CharField(max_length=50, verbose_name='机器序列号')
    batch_number = models.CharField(max_length=50, verbose_name='批次号')
    manufactory = models.CharField(max_length=50, verbose_name='工厂')
    goods_id = models.CharField(max_length=30, verbose_name='型号')
    appraisal = models.CharField(max_length=200, verbose_name='保修结束语')


    class Meta:
        verbose_name = '维修序列号列表'
        verbose_name_plural = verbose_name
        db_table = 'oms_m_faultmachinesn'

    def __str__(self):
        return self.m_sn


class GoodFaultSummary(BaseModel):
    statistic_time = models.DateTimeField(verbose_name='统计时间')
    production_quantity = models.IntegerField(default=0, verbose_name='生产数量')
    production_cumulation = models.IntegerField(default=0, verbose_name='生产累计数量')
    fault_quantity = models.IntegerField(default=0, verbose_name='故障数量')
    fault_cumulation = models.IntegerField(default=0, verbose_name='故障累计数量')
    goods_id = models.CharField(max_length=30, verbose_name='型号')

    class Meta:
        verbose_name = '机器故障数量汇总表'
        verbose_name_plural = verbose_name
        db_table = 'oms_m_goodfaultsummary'

    def __str__(self):
        return self.goods_id


class FactoryFaultSummary(BaseModel):
    statistic_time = models.DateTimeField(verbose_name='统计时间')
    manufactory = models.CharField(max_length=50, verbose_name='工厂')
    cumulation = models.IntegerField(verbose_name='生产数量累计')

    class Meta:
        verbose_name = '工厂故障数量汇总表'
        verbose_name_plural = verbose_name
        db_table = 'oms_m_factoryfaultsummary'

    def __str__(self):
        return self.manufactory


class BatchFaultSummary(BaseModel):
    statistic_time = models.DateTimeField(verbose_name='统计时间')
    batch_number = models.CharField(max_length=50, verbose_name='批次号')
    fault_cumulation = models.IntegerField(verbose_name='故障数量累计')
    cumulation = models.IntegerField(verbose_name='生产数量累计')


    class Meta:
        verbose_name = '批次故障数量统计表'
        verbose_name_plural = verbose_name
        db_table = 'oms_m_batchfaultsummary'

    def __str__(self):
        return self.batch_number


class GoodsInfo(BaseModel):
    GOODS_TYPE = (
        ("VAC", "吸尘器"),
        ("DMC", "除螨仪"),
        ("VAR", "智能机器人"),
        ("OTH", "其他"),
    )

    GOODS_ATTRIBUTE = (
        (0, "整机"),
        (1, "配件"),
        (2, "礼品"),
    )

    goods_id = models.CharField(unique=True, max_length=30, verbose_name='货品编码', db_index=True)
    goods_name = models.CharField(unique=True, max_length=60, verbose_name='货品名称', db_index=True)
    category = models.CharField(choices=GOODS_TYPE, default="OTH", max_length=10, verbose_name='货品类别')
    goods_attribute = models.IntegerField(choices=GOODS_ATTRIBUTE, default=0, verbose_name='货品属性')
    goods_number = models.CharField(unique=True, max_length=10, verbose_name='机器排序')
    size = models.CharField(null=True, blank=True, max_length=50, verbose_name='规格')
    width = models.IntegerField(null=True, blank=True, verbose_name='长')
    height = models.IntegerField(null=True, blank=True, verbose_name='宽')
    depth = models.IntegerField(null=True, blank=True, verbose_name='高')
    weight = models.IntegerField(null=True, blank=True, verbose_name='重量')

    class Meta:
        verbose_name = '货品信息表'
        verbose_name_plural = verbose_name
        db_table = 'oms_m_goodsinfo'

    def __str__(self):
        return self.goods_name


class PartInfo(GoodsInfo):
    class Meta:
        verbose_name = '配件信息表'
        verbose_name_plural = verbose_name
        proxy = True

    def __str__(self):
        return self.goods_name


class MachineInfo(GoodsInfo):
    class Meta:
        verbose_name = '机器信息表'
        verbose_name_plural = verbose_name
        proxy = True

    def __str__(self):
        return self.goods_name

















