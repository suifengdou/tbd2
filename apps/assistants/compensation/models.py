# -*- coding: utf-8 -*-
# @Time    : 2020/09/17 13:47
# @Author  : Hann
# @Site    :
# @File    : urls.py.py
# @Software: PyCharm

from django.db import models
from django.db.models import Sum, Avg, Min, Max, F
import django.utils.timezone as timezone

from db.base_model import BaseModel
from apps.crm.dialog.models import OriDetailTB


class OriCompensation(BaseModel):
    ORDERSTATUS = (
        (0, '已取消'),
        (1, '未处理'),
        (2, '已完成'),
    )
    ORDER_CATEGORY = (
        (1, '差价补偿'),
        (2, '错误重置'),
        (3, '退货退款'),
    )
    MISTAKE_LIST = (
        (0, '正常'),
        (1, '重复建单'),
        (2, '特殊订单才能追加'),
        (3, '追加单保存出错'),
        (4, '实收减应收不等于校验金额'),
        (5, '差价金额不等于校验金额'),
        (6, '恢复单保存出错'),
        (7, '补偿单保存出错'),
        (8, '相同单号存在多个差价，需要设置特殊订单'),
        (9, '相同单号存在多个差价，需要设置特殊订单'),
    )
    PROCESS_TAG = (
        (0, '未处理'),
        (1, '待核实'),
        (2, '已确认'),
        (3, '待清账'),
        (4, '已处理'),
        (5, '特殊订单'),
        (6, '重置'),
    )
    servicer = models.CharField(max_length=50, verbose_name='客服')
    shop = models.CharField(max_length=60, verbose_name='店铺')
    goods_name = models.CharField(max_length=50, verbose_name='货品名称')
    nickname = models.CharField(max_length=50, verbose_name='用户网名', db_index=True)
    order_id = models.CharField(max_length=60, verbose_name='订单号', db_index=True)
    order_category = models.SmallIntegerField(choices=ORDER_CATEGORY, default=1, verbose_name='单据类型')
    compensation = models.FloatField(verbose_name='补偿金额')
    name = models.CharField(max_length=150, verbose_name='姓名', db_index=True)
    alipay_id = models.CharField(max_length=150, verbose_name='支付宝', db_index=True)
    actual_receipts = models.FloatField(verbose_name='实收金额')
    receivable = models.FloatField(verbose_name='应收金额')
    checking = models.FloatField(verbose_name='验算结果')
    memorandum = models.TextField(blank=True, null=True, verbose_name='备注')

    order_status = models.IntegerField(choices=ORDERSTATUS, default=1, verbose_name='单据状态')
    process_tag = models.IntegerField(choices=PROCESS_TAG, default=0, verbose_name='处理标签')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误列表')
    handler = models.CharField(null=True, blank=True, max_length=30, verbose_name='处理人')
    handle_time = models.DateTimeField(null=True, blank=True, verbose_name='处理时间')

    class Meta:
        verbose_name = 'CRM-原始补偿单-查询'
        verbose_name_plural = verbose_name
        db_table = 'ass_compen_ori'

    def __str__(self):
        return str(self.alipay_id)


class OCCheck(OriCompensation):

    class Meta:
        verbose_name = 'CRM-原始补偿单-未审核'
        verbose_name_plural = verbose_name
        proxy = True


class Compensation(BaseModel):
    ORDERSTATUS = (
        (0, '已取消'),
        (1, '未处理'),
        (2, '已完成'),
    )

    MISTAKE_LIST = (
        (0, '正常'),
        (1, '汇总单保存出错'),
        (2, '汇总单明细保存出错'),
        (3, '无店铺'),
        (4, '补寄配件记录格式错误'),
        (5, '补寄原因错误'),
        (6, '单据创建失败'),
    )
    PROCESS_TAG = (
        (0, '未处理'),
        (1, '待核实'),
        (2, '已确认'),
        (3, '待清账'),
        (4, '已处理'),
        (5, '特殊订单'),
    )
    servicer = models.CharField(max_length=50, verbose_name='客服')
    shop = models.CharField(max_length=60, verbose_name='店铺')
    goods_name = models.TextField(verbose_name='货品名称')
    nickname = models.CharField(max_length=50, verbose_name='用户网名', db_index=True)
    order_id = models.TextField(verbose_name='订单号')
    compensation = models.FloatField(verbose_name='补偿金额')
    name = models.CharField(max_length=150, verbose_name='姓名', db_index=True)
    alipay_id = models.CharField(max_length=150, verbose_name='支付宝', db_index=True)
    actual_receipts = models.FloatField(verbose_name='实收金额')
    receivable = models.FloatField(verbose_name='应收金额')
    checking = models.FloatField(verbose_name='验算结果')
    memorandum = models.TextField(blank=True, null=True, verbose_name='备注')

    order_status = models.IntegerField(choices=ORDERSTATUS, default=1, verbose_name='单据状态')
    process_tag = models.IntegerField(choices=PROCESS_TAG, default=0, verbose_name='处理标签')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误列表')
    handler = models.CharField(null=True, blank=True, max_length=30, verbose_name='处理人')
    handle_time = models.DateTimeField(null=True, blank=True, verbose_name='处理时间')

    class Meta:
        verbose_name = 'CRM-补偿单-查询'
        verbose_name_plural = verbose_name
        db_table = 'ass_compen'

    def __str__(self):
        return str(self.alipay_id)


class CCheck(Compensation):
    class Meta:
        verbose_name = 'CRM-补偿单-未审核'
        verbose_name_plural = verbose_name
        proxy = True


class OriToCList(BaseModel):

    ORDERSTATUS = (
        (0, '已取消'),
        (1, '已生成'),
    )
    ori_order = models.OneToOneField(OriCompensation, on_delete=models.CASCADE, verbose_name='原始补偿单')
    order = models.ForeignKey(Compensation, on_delete=models.CASCADE, verbose_name='补偿单')
    order_status = models.IntegerField(choices=ORDERSTATUS, default=1, verbose_name='单据状态')

    class Meta:
        verbose_name = 'CRM-补偿单验算表-查询'
        verbose_name_plural = verbose_name
        db_table = 'ass_compen_list'

    def __str__(self):
        return str(self.order)


class DiaToOriist(BaseModel):

    ORDERSTATUS = (
        (0, '已取消'),
        (1, '已生成'),
    )
    ori_order = models.OneToOneField(OriCompensation, on_delete=models.CASCADE, related_name='com_create', verbose_name='原始补偿单')
    dialog_order = models.OneToOneField(OriDetailTB, on_delete=models.CASCADE, related_name='com_dialog_tb', verbose_name='对话明细')

    class Meta:
        verbose_name = 'CRM-补偿单提取对照表-查询'
        verbose_name_plural = verbose_name
        db_table = 'ass_compen_dia2ori'

    def __str__(self):
        return str(self.ori_order)


class BatchCompensation(BaseModel):
    ORDERSTATUS = (
        (0, '已取消'),
        (1, '未处理'),
        (2, '未结算'),
        (3, '已完成'),
    )

    MISTAKE_LIST = (
        (0, '正常'),
        (1, '无OA单号'),
        (2, '先设置订单已完成再审核'),
        (3, '已递交过此OA单号'),
        (4, '补寄配件记录格式错误'),
        (5, '补寄原因错误'),
        (6, '单据创建失败'),
    )
    PROCESS_TAG = (
        (0, '未处理'),
        (1, '待核实'),
        (2, '已确认'),
        (3, '待清账'),
        (4, '已处理'),
        (5, '特殊订单'),
    )
    order_id = models.CharField(max_length=60, verbose_name='批次单号')
    quantity = models.IntegerField(verbose_name='补偿单数量')
    oa_order_id = models.CharField(null=True, blank=True, max_length=60, verbose_name='OA单号')
    handler = models.CharField(null=True, blank=True, max_length=30, verbose_name='处理人')
    handle_time = models.DateTimeField(null=True, blank=True, verbose_name='处理时间')

    order_status = models.IntegerField(choices=ORDERSTATUS, default=1, verbose_name='单据状态')
    process_tag = models.IntegerField(choices=PROCESS_TAG, default=0, verbose_name='处理标签')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误列表')

    class Meta:
        verbose_name = 'CRM-补偿汇总单-查询'
        verbose_name_plural = verbose_name
        db_table = 'ass_compen_batch'

    def __str__(self):
        return str(self.order_id)

    def amount(self):
        amount = self.batchinfo_set.all().aggregate(amount=Sum('paid_amount'))['amount']
        if not amount:
            return 0
        return amount
    amount.short_description = '补偿总金额'


class BSubmit(BatchCompensation):
    class Meta:
        verbose_name = 'CRM-补偿汇总单-未审核'
        verbose_name_plural = verbose_name
        proxy = True


class BCheck(BatchCompensation):
    class Meta:
        verbose_name = 'CRM-补偿汇总单-未结算'
        verbose_name_plural = verbose_name
        proxy = True



class BatchInfo(BaseModel):

    MISTAKE_LIST = (
        (0, '正常'),
        (1, '已付金额不是零，不可重置'),
        (2, '重置保存补偿单出错'),
        (3, '补运费和已付不相等'),
        (4, '补寄配件记录格式错误'),
        (5, '补寄原因错误'),
        (6, '单据创建失败'),
    )
    PROCESS_TAG = (
        (0, '未处理'),
        (1, '待核实'),
        (2, '已确认'),
        (3, '待清账'),
        (4, '已处理'),
        (5, '特殊订单'),
    )

    batch_order = models.ForeignKey(BatchCompensation, on_delete=models.CASCADE, verbose_name='批次单')
    compensation_order = models.OneToOneField(Compensation, on_delete=models.CASCADE, verbose_name='补偿单')
    servicer = models.CharField(max_length=50, verbose_name='客服')
    shop = models.CharField(max_length=60, verbose_name='店铺')
    goods_name = models.TextField(verbose_name='货品名称')
    nickname = models.CharField(max_length=50, verbose_name='用户网名', db_index=True)
    order_id = models.TextField(verbose_name='订单号')
    compensation = models.FloatField(verbose_name='补偿金额')
    paid_amount = models.FloatField(default=0, verbose_name='已付金额')
    name = models.CharField(max_length=150, verbose_name='姓名', db_index=True)
    alipay_id = models.CharField(max_length=150, verbose_name='支付宝', db_index=True)
    actual_receipts = models.FloatField(verbose_name='实收金额')
    receivable = models.FloatField(verbose_name='应收金额')
    checking = models.FloatField(verbose_name='验算结果')
    memorandum = models.TextField(blank=True, null=True, verbose_name='备注')

    process_tag = models.IntegerField(choices=PROCESS_TAG, default=0, verbose_name='处理标签')
    mistake_tag = models.SmallIntegerField(choices=MISTAKE_LIST, default=0, verbose_name='错误列表')

    class Meta:
        verbose_name = 'CRM-补偿汇总明细单-查询'
        verbose_name_plural = verbose_name
        db_table = 'ass_compen_batchinfro'

    def __str__(self):
        return str(self.batch_order)

    def oa_order_id(self):
        oa_order_id = self.batch_order.oa_order_id
        return str(oa_order_id)
    oa_order_id.short_description = 'OA单号'


class BICheck(BatchInfo):
    class Meta:
        verbose_name = 'CRM-补偿汇总明细单-未结算'
        verbose_name_plural = verbose_name
        proxy = True


