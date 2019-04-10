# -*- coding: utf-8 -*-
# @Time    : 2018/11/26 13:47
# @Author  : Hann
# @Site    :
# @File    : urls.py.py
# @Software: PyCharm


from django.db import models


from db.base_model import BaseModel


class SFConsignation(BaseModel):
    VERIFY_FIELD = ['application_time', 'consignor', 'information', 'is_operate', 'feedback_time', 'express_id']
    ODER_STATUS = (
        (0, '未审核'),
        (1, '已处理'),
        (2, '已完结'),
    )

    application_time = models.CharField(max_length=20, verbose_name='日期')
    consignor = models.CharField(max_length=30, verbose_name='委托人')
    information = models.CharField(max_length=600, verbose_name='信息')
    remark = models.CharField(null=True, blank=True, max_length=300, verbose_name='异常知会')
    is_operate = models.CharField(max_length=20, verbose_name="是否操作")
    feedback_time = models.CharField(max_length=20, verbose_name='反馈日期')
    express_id = models.CharField(max_length=100, verbose_name='单号')
    handlingstatus = models.SmallIntegerField(choices=ODER_STATUS, verbose_name='委托单状态', default=0)

    class Meta:
        verbose_name = '顺丰委托单'
        verbose_name_plural = verbose_name
        db_table = 'sfconsignation'

    def __str__(self):
        return self.express_id

    @classmethod
    def verify_mandatory(cls, columns_key):
        for i in cls.VERIFY_FIELD:
            if i not in columns_key:
                return 'verify_field error, must have mandatory field: "{}""'.format(i)
        else:
            return None