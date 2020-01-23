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
from apps.base.company.models import WareInfo


class WorkOrder3PL(BaseModel):
    VERIFY_FIELD = ['keyword', 'information', 'category']
    ORDER_STATUS = (
        (0, '已被取消'),
        (1, '逆向未递'),
        (2, '逆向未理'),
        (3, '正向未递'),
        (4, '仓储未理'),
        (5, '复核未理'),
        (6, '财务审核'),
        (7, '工单完结'),
    )
    CATEGORY = (
        (0, '入库错误'),
        (1, '系统问题'),
        (2, '单据问题'),
        (3, '订单类别'),
        (4, '入库咨询'),
        (5, '出库咨询'),
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

    keyword = models.CharField(unique=True, max_length=100, verbose_name='事务关键字')
    information = models.TextField(max_length=600, verbose_name='初始问题信息')
    submit_time = models.DateTimeField(null=True, blank=True, verbose_name='客服提交时间')
    servicer = models.CharField(null=True, blank=True, max_length=60, verbose_name='客服')
    services_interval = models.IntegerField(null=True, blank=True, verbose_name='客服处理间隔(分钟)')

    handler = models.CharField(null=True, blank=True, max_length=30, verbose_name='供应处理人')
    handle_time = models.DateTimeField(null=True, blank=True, verbose_name='供应处理时间')
    express_interval = models.IntegerField(null=True, blank=True, verbose_name='供应处理间隔(分钟)')
    feedback = models.TextField(null=True, blank=True, max_length=900, verbose_name='逆向反馈内容')
    is_losing = models.SmallIntegerField(choices=LOGICAL_DEXISION, default=0, verbose_name='是否涉及理赔')

    return_express_id = models.CharField(null=True, blank=True, max_length=200, verbose_name='正向反馈内容')
    is_return = models.IntegerField(choices=LOGICAL_DEXISION, default=1, verbose_name='是否反馈')
    memo = models.TextField(null=True, blank=True, verbose_name='备注')

    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='工单状态')
    category = models.SmallIntegerField(choices=CATEGORY, default=0, verbose_name='工单事项类型')
    wo_category = models.SmallIntegerField(choices=WO_CATEGORY, default=0, verbose_name='工单类型')
    company = models.ForeignKey(WareInfo, on_delete=models.CASCADE, null=True, blank=True, verbose_name='供应商')

    class Meta:
        verbose_name = 'EXT-仓储工单-查询'
        verbose_name_plural = verbose_name
        db_table = 'ext_workorder3pl'

    def __str__(self):
        return self.keyword

    @classmethod
    def verify_mandatory(cls, columns_key):
        for i in cls.VERIFY_FIELD:
            if i not in columns_key:
                return 'verify_field error, must have mandatory field: "{}""'.format(i)
        else:
            return None


class WorkOrder3PLAppRev(WorkOrder3PL):
    class Meta:
        verbose_name = 'EXT-仓储工单-逆向'
        verbose_name_plural = verbose_name
        proxy = True


class WorkOrder3PLApp(WorkOrder3PL):
    class Meta:
        verbose_name = 'EXT-仓储工单-正向'
        verbose_name_plural = verbose_name
        proxy = True


class WorkOrder3PLHandle(WorkOrder3PL):
    class Meta:
        verbose_name = 'EXT-仓储工单处理'
        verbose_name_plural = verbose_name
        proxy = True


class WorkOrder3PLHandleSto(WorkOrder3PL):
    class Meta:
        verbose_name = 'EXT-仓储工单处理-供应商'
        verbose_name_plural = verbose_name
        proxy = True


class WorkOrder3PLKeshen(WorkOrder3PL):
    class Meta:
        verbose_name = 'EXT-仓储工单复核'
        verbose_name_plural = verbose_name
        proxy = True


class WorkOrder3PLMine(WorkOrder3PL):
    class Meta:
        verbose_name = 'EXT-仓储工单-财务审核'
        verbose_name_plural = verbose_name
        proxy = True


class WorkOrder3PLProcess(WorkOrder3PL):
    class Meta:
        verbose_name = 'EXT-仓储工单-未完结'
        verbose_name_plural = verbose_name
        proxy = True