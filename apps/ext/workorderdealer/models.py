# -*- coding: utf-8 -*-
# @Time    : 2020/2/5 9:27
# @Author  : Hann
# @Site    :
# @File    : models.py
# @Software: PyCharm

from django.db import models
import django.utils.timezone as timezone

from db.base_model import BaseModel
from apps.base.company.models import DealerInfo
from apps.base.goods.models import MachineInfo


class WorkOrder(BaseModel):
    VERIFY_FIELD = ['order_id', 'information', 'category']
    ORDER_STATUS = (
        (0, '已被取消'),
        (1, '经销未递'),
        (2, '客服在理'),
        (3, '经销复核'),
        (4, '运营对账'),
        (5, '工单完结'),
    )
    PROCESSTAG = (
        (0, '未处理'),
        (1, '待核实'),
        (2, '已在途'),
        (3, '收异常'),
        (4, '未退回'),
        (5, '丢件核'),
        (6, '纠纷中'),
        (7, '其他'),

    )
    MISTAKE_LIST = (
        (0, '正常'),
        (1, '返回单号为空'),
        (2, '处理意见为空'),
        (3, '正常'),
        (4, '正常'),
        (5, '正常'),
        (6, '正常'),
        (7, '正常'),
        (8, '正常'),
    )

    WO_CATEGORY = (
        (0, '退货'),
        (1, '换货'),
    )

    LOGICAL_DEXISION = (
        (0, '否'),
        (1, '是'),
    )

    order_id = models.CharField(unique=True, max_length=100, verbose_name='源订单单号')
    information = models.TextField(max_length=600, verbose_name='初始问题信息')
    memo = models.TextField(null=True, blank=True, verbose_name='经销商反馈')
    goods_name = models.ForeignKey(MachineInfo, on_delete=models.CASCADE, verbose_name='机器型号')
    quantity = models.IntegerField(verbose_name='数量')
    amount = models.FloatField(verbose_name='合计金额')
    wo_category = models.SmallIntegerField(choices=WO_CATEGORY, default=0, verbose_name='工单类型')
    is_customer_post = models.SmallIntegerField(choices=LOGICAL_DEXISION, default=0, verbose_name='是否客户邮寄')
    return_express_company = models.CharField(null=True, blank=True, max_length=100, verbose_name='返回快递公司')
    return_express_id = models.CharField(null=True, blank=True, max_length=100, verbose_name='返回单号')

    submit_time = models.DateTimeField(null=True, blank=True, verbose_name='客服提交时间')
    servicer = models.CharField(null=True, blank=True, max_length=60, verbose_name='客服')
    services_interval = models.IntegerField(null=True, blank=True, verbose_name='客服处理间隔(分钟)')
    is_losing = models.SmallIntegerField(choices=LOGICAL_DEXISION, default=0, verbose_name='是否丢件')
    feedback = models.TextField(null=True, blank=True, max_length=900, verbose_name='客服处理意见')

    handler = models.CharField(null=True, blank=True, max_length=30, verbose_name='经销商处理人')
    handle_time = models.DateTimeField(null=True, blank=True, verbose_name='经销商处理时间')
    express_interval = models.IntegerField(null=True, blank=True, verbose_name='经销商处理间隔(分钟)')

    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='工单状态')

    company = models.ForeignKey(DealerInfo, on_delete=models.CASCADE, null=True, blank=True, related_name='dealer', verbose_name='经销商')
    process_tag = models.SmallIntegerField(choices=PROCESSTAG, default=0, verbose_name='处理标签')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误原因')

    class Meta:
        verbose_name = 'EXT-经销商工单-查询'
        verbose_name_plural = verbose_name
        db_table = 'ext_workorderdealer'

    def __str__(self):
        return self.order_id

    @classmethod
    def verify_mandatory(cls, columns_key):
        for i in cls.VERIFY_FIELD:
            if i not in columns_key:
                return 'verify_field error, must have mandatory field: "{}""'.format(i)
        else:
            return None


class WOCreate(WorkOrder):
    class Meta:
        verbose_name = 'EXT-经销商工单-创建'
        verbose_name_plural = verbose_name
        proxy = True


class WOService(WorkOrder):
    class Meta:
        verbose_name = 'EXT-经销商工单-客服'
        verbose_name_plural = verbose_name
        proxy = True


class WODealer(WorkOrder):
    class Meta:
        verbose_name = 'EXT-经销商工单-经销商'
        verbose_name_plural = verbose_name
        proxy = True


class WOOperator(WorkOrder):
    class Meta:
        verbose_name = 'EXT-经销商工单-运营'
        verbose_name_plural = verbose_name
        proxy = True


class WOTrack(WorkOrder):
    class Meta:
        verbose_name = 'EXT-经销商工单-跟进'
        verbose_name_plural = verbose_name
        proxy = True

