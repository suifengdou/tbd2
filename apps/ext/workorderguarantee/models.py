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


class WOCategory(BaseModel):
    ORDER_STATUS = (
        (0, '已取消'),
        (1, '正常'),
    )
    name = models.CharField(max_length=30, verbose_name='类别名称', unique=True, db_index=True)
    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='工单状态')

    class Meta:
        verbose_name = 'EXT-技术工单-工单类别'
        verbose_name_plural = verbose_name
        db_table = 'ext_workordergu_category'

    def __str__(self):
        return self.name



class WorkOrder(BaseModel):

    ORDER_STATUS = (
        (0, '已被取消'),
        (1, '技术未递'),
        (2, '正向未递'),
        (3, '客服在理'),
        (4, '技术未理'),
        (5, '终审未理'),
        (6, '工单完结'),
    )

    WO_CATEGORY = (
        (0, '正向工单'),
        (1, '逆向工单'),
    )

    LOGICAL_DEXISION = (
        (0, '否'),
        (1, '是'),
    )
    PROCESSTAG = (
        (0, '未分类'),
        (1, '待截单'),
        (2, '签复核'),
        (3, '改地址'),
        (4, '催派查'),
        (5, '丢件核'),
        (6, '纠纷中'),
        (7, '其他'),

    )
    MISTAKE_LIST = (
        (0, '正常'),
        (1, '无发票号'),
        (2, '快递单错误'),
        (3, '快递未发货'),
        (4, '驳回出错'),

    )

    express_id = models.CharField(unique=True, max_length=100, verbose_name='快递单号', db_index=True)
    goods_name = models.ForeignKey(MachineInfo, on_delete=models.CASCADE, related_name='g_goods_name', verbose_name='型号')
    information = models.TextField(max_length=600, verbose_name='初始问题信息')
    submit_time = models.DateTimeField(null=True, blank=True, verbose_name='技术提交时间')
    servicer = models.CharField(null=True, blank=True, max_length=60, verbose_name='技术')
    services_interval = models.IntegerField(null=True, blank=True, verbose_name='技术处理间隔(分钟)')
    servicer_feedback = models.TextField(null=True, blank=True, verbose_name='技术反馈')

    handler = models.CharField(null=True, blank=True, max_length=30, verbose_name='客服处理人')
    handle_time = models.DateTimeField(null=True, blank=True, verbose_name='客服处理时间')
    process_interval = models.IntegerField(null=True, blank=True, verbose_name='客服处理间隔(分钟)')
    feedback = models.TextField(null=True, blank=True, max_length=900, verbose_name='反馈内容')

    memo = models.TextField(null=True, blank=True, verbose_name='备注')

    order_status = models.SmallIntegerField(choices=ORDER_STATUS, default=1, verbose_name='工单状态')
    category = models.ForeignKey(WOCategory, on_delete=models.CASCADE, verbose_name='工单事项类型')
    wo_category = models.SmallIntegerField(choices=WO_CATEGORY, default=0, verbose_name='工单类型')
    process_tag = models.SmallIntegerField(choices=PROCESSTAG, default=0, verbose_name='处理标签')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='异常原因')

    class Meta:
        verbose_name = 'EXT-技术工单-查询'
        verbose_name_plural = verbose_name
        db_table = 'ext_workordergu_order'

    def __str__(self):
        return self.express_id


class WORCreate(WorkOrder):
    class Meta:
        verbose_name = 'EXT-技术工单-逆向创建'
        verbose_name_plural = verbose_name
        proxy = True


class WOPCreate(WorkOrder):
    class Meta:
        verbose_name = 'EXT-技术工单-正向创建'
        verbose_name_plural = verbose_name
        proxy = True


class WOSCheck(WorkOrder):
    class Meta:
        verbose_name = 'EXT-技术工单-客服审核'
        verbose_name_plural = verbose_name
        proxy = True


class WORCheck(WorkOrder):
    class Meta:
        verbose_name = 'EXT-技术工单-技术审核'
        verbose_name_plural = verbose_name
        proxy = True


class WOFinish(WorkOrder):
    class Meta:
        verbose_name = 'EXT-技术工单-终审确认'
        verbose_name_plural = verbose_name
        proxy = True



