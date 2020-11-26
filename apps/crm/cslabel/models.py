# -*- coding:  utf-8 -*-
# @Time    :  2020/11/19 13: 47
# @Author  :  Hann
# @Site    : 
# @File    :  urls.py.py
# @Software:  PyCharm


from django.db import models

from db.base_model import BaseModel
from apps.crm.customers.models import CustomerInfo


class LabelInfo(BaseModel):

    ORDERSTATUS = (
        (0, '已取消'),
        (1, '正常'),
    )
    ORDER_CATEGORY = (
        (1, "常规类型"),
        (2, "特殊类型"),
        (3, "自动创建"),
    )

    name = models.CharField(max_length=120, unique=True, db_index=True, verbose_name='标签名称')
    order_category = models.SmallIntegerField(choices=ORDER_CATEGORY, default=1, db_index=True, verbose_name='标签类型')
    memorandum = models.CharField(max_length=220, verbose_name='标签说明')
    order_status = models.SmallIntegerField(choices=ORDERSTATUS, default=1, db_index=True, verbose_name='单据状态')

    class Meta:
        verbose_name = 'CRM-标签-标签管理'
        verbose_name_plural = verbose_name
        db_table = 'crm_label_label'

    def __str__(self):
        return str(self.name)


class LabelOrder(BaseModel):

    ORDERSTATUS = (
        (0, '已取消'),
        (1, '未关联'),
        (2, '已完成'),
    )
    MISTAKE_LIST = (
        (0, '正常'),
        (1, '个别明细单出错，无法审核'),
    )

    order_id = models.CharField(max_length=150, unique=True, verbose_name='单据编号')
    label = models.ForeignKey(LabelInfo, on_delete=models.CASCADE, blank=True, null=True, verbose_name='标签')
    quantity = models.IntegerField(verbose_name='客户数量')
    order_status = models.SmallIntegerField(choices=ORDERSTATUS, default=1, db_index=True, verbose_name='单据状态')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误列表')
    service_num = models.IntegerField(default=0, verbose_name='关联任务次数')

    class Meta:
        verbose_name = 'CRM-标签关联单-查询'
        verbose_name_plural = verbose_name
        db_table = 'crm_label_order'

    def __str__(self):
        return str(self.order_id)


class AssociateLabel(LabelOrder):

    class Meta:
        verbose_name = 'CRM-标签关联单-待关联'
        verbose_name_plural = verbose_name
        proxy = True


class LabelDetial(BaseModel):
    ORDERSTATUS = (
        (0, '已取消'),
        (1, '待关联'),
        (2, '已完成'),
    )
    MISTAKE_LIST = (
        (0, '正常'),
        (1, '已存在标记，不可重复标记'),
    )

    label_order = models.ForeignKey(LabelOrder, on_delete=models.CASCADE, verbose_name='标签关联单')
    customer = models.ForeignKey(CustomerInfo, on_delete=models.CASCADE, verbose_name='客户')
    order_status = models.SmallIntegerField(choices=ORDERSTATUS, default=1, db_index=True, verbose_name='单据状态')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误列表')
    service_num = models.IntegerField(default=0, verbose_name='关联任务次数')

    class Meta:
        verbose_name = 'CRM-标签关联明细单-查询'
        verbose_name_plural = verbose_name
        db_table = 'crm_label_orderdetail'
        unique_together = ('label_order', 'customer')

    def __str__(self):
        return str(self.customer)


class AssociateLabelDetial(LabelDetial):

    class Meta:
        verbose_name = 'CRM-标签关联明细单-待关联'
        verbose_name_plural = verbose_name
        proxy = True


class LabelResult(BaseModel):
    ORDERSTATUS = (
        (0, '已取消'),
        (1, '待关联'),
        (2, '已完成'),
    )
    MISTAKE_LIST = (
        (0, '正常'),
    )

    label_order = models.ForeignKey(LabelOrder, on_delete=models.CASCADE, verbose_name='标签关联单')
    label = models.ForeignKey(LabelInfo, on_delete=models.CASCADE, blank=True, null=True, verbose_name='标签')
    customer = models.ForeignKey(CustomerInfo, on_delete=models.CASCADE, verbose_name='客户')
    order_status = models.SmallIntegerField(choices=ORDERSTATUS, default=1, db_index=True, verbose_name='单据状态')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误列表')
    service_num = models.IntegerField(default=0, verbose_name='关联任务次数')

    class Meta:
        verbose_name = 'CRM-标签-完整明细查询'
        verbose_name_plural = verbose_name
        db_table = 'crm_label_result'
        unique_together = ('label', 'customer')

    def __str__(self):
        return str(self.customer)

