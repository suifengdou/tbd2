# -*- coding: utf-8 -*-
# @Time    : 2018/11/26 13:47
# @Author  : Hann
# @Site    :
# @File    : urls.py.py
# @Software: PyCharm

from django.db import models
import django.utils.timezone as timezone

from db.base_model import BaseModel
from apps.base.goods.models import MachineInfo
from apps.base.company.models import LogisticsInfo


class WorkOrder(BaseModel):
    VERIFY_FIELD = ['express_id', 'information', 'category']
    ORDER_STATUS = (
        (0, '已被取消'),
        (1, '快递未递'),
        (2, '逆向未理'),
        (3, '正向未递'),
        (4, '快递未理'),
        (5, '复核未理'),
        (6, '工单完结'),
    )
    CATEGORY = (
        (0, '截单退回'),
        (1, '无人收货'),
        (2, '客户拒签'),
        (3, '修改地址'),
        (4, '催件派送'),
        (5, '虚假签收'),
        (6, '其他异常'),
    )
    WO_CATEGORY = (
        (0, '正向工单'),
        (1, '逆向工单'),
    )
    COMPANY = (
        (0, '申通'),
    )
    LOGICAL_DEXISION = (
        (0, '否'),
        (1, '是'),
    )

    express_id = models.CharField(unique=True, max_length=100, verbose_name='源单号')
    information = models.TextField(max_length=600, verbose_name='初始问题信息')
    submit_time = models.DateTimeField(null=True, blank=True, verbose_name='客服提交时间')
    servicer = models.CharField(null=True, blank=True, max_length=60, verbose_name='客服')
    services_interval = models.IntegerField(null=True, blank=True, verbose_name='客服处理间隔(分钟)')

    handler = models.CharField(null=True, blank=True, max_length=30, verbose_name='快递处理人')
    handle_time = models.DateTimeField(null=True, blank=True, verbose_name='快递处理时间')
    express_interval = models.IntegerField(null=True, blank=True, verbose_name='快递处理间隔(分钟)')
    feedback = models.TextField(null=True, blank=True, max_length=900, verbose_name='反馈内容')
    is_losing = models.SmallIntegerField(choices=LOGICAL_DEXISION, default=0, verbose_name='是否丢件')

    return_express_id = models.CharField(null=True, blank=True, max_length=100, verbose_name='返回单号')
    is_return = models.IntegerField(choices=LOGICAL_DEXISION, default=1, verbose_name='是否返回')
    memo = models.TextField(null=True, blank=True, verbose_name='备注')

    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='工单状态')
    category = models.SmallIntegerField(choices=CATEGORY, default=0, verbose_name='工单事项类型')
    wo_category = models.SmallIntegerField(choices=WO_CATEGORY, default=0, verbose_name='工单类型')
    company = models.ForeignKey(LogisticsInfo, on_delete=models.CASCADE, null=True, blank=True, verbose_name='快递公司')

    class Meta:
        verbose_name = 'EXT-快递工单-查询'
        verbose_name_plural = verbose_name
        db_table = 'ext_workorderex'

    def __str__(self):
        return self.express_id

    @classmethod
    def verify_mandatory(cls, columns_key):
        for i in cls.VERIFY_FIELD:
            if i not in columns_key:
                return 'verify_field error, must have mandatory field: "{}""'.format(i)
        else:
            return None


class WorkOrderAppRev(WorkOrder):
    VERIFY_FIELD = ['express_id', 'information', 'category']
    class Meta:
        verbose_name = 'EXT-快递工单-逆向'
        verbose_name_plural = verbose_name
        proxy = True

    @classmethod
    def verify_mandatory(cls, columns_key):
        for i in cls.VERIFY_FIELD:
            if i not in columns_key:
                return 'verify_field error, must have mandatory field: "{}""'.format(i)
        else:
            return None


class WorkOrderApp(WorkOrder):
    VERIFY_FIELD = ['express_id', 'information', 'category', 'company']
    class Meta:
        verbose_name = 'EXT-快递工单-正向'
        verbose_name_plural = verbose_name
        proxy = True

    @classmethod
    def verify_mandatory(cls, columns_key):
        for i in cls.VERIFY_FIELD:
            if i not in columns_key:
                return 'verify_field error, must have mandatory field: "{}""'.format(i)
        else:
            return None


class WorkOrderHandle(WorkOrder):
    class Meta:
        verbose_name = 'EXT-快递工单处理-客服'
        verbose_name_plural = verbose_name
        proxy = True


class WorkOrderHandleSto(WorkOrder):
    class Meta:
        verbose_name = 'EXT-快递工单处理-供应商'
        verbose_name_plural = verbose_name
        proxy = True


class WorkOrderKeshen(WorkOrder):
    class Meta:
        verbose_name = 'EXT-快递工单复核-客审'
        verbose_name_plural = verbose_name
        proxy = True


class WorkOrderMine(WorkOrder):
    class Meta:
        verbose_name = 'EXT-快递工单-只看自己'
        verbose_name_plural = verbose_name
        proxy = True



