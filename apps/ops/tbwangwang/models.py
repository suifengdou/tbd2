# -*- coding:  utf-8 -*-
# @Time    :  2019/5/11 13: 47
# @Author  :  Hann
# @Site    :
# @File    :  models.py
# @Software:  PyCharm

from django.db import models
import django.utils.timezone as timezone
import pandas as pd

from db.base_model import BaseModel
from apps.base.shop.models import ShopInfo

class FilterationWWInfo(BaseModel):
    ORDERSTATUS = (
        (0, '已取消'),
        (1, '未处理'),
        (2, '已完成'),
    )

    dialog_time = models.DateTimeField(verbose_name='聊天时间')
    buyer_ww = models.CharField(max_length=60, verbose_name='买家旺旺')
    start_time = models.TimeField(verbose_name='开始时间')
    end_time = models.TimeField(verbose_name='结束时间')
    cs_ww = models.CharField(max_length=60, verbose_name='客服旺旺')
    filter_category = models.CharField(max_length=30, verbose_name='过滤类型')
    shop = models.ForeignKey(ShopInfo, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='店铺')
    status = models.IntegerField(choices=ORDERSTATUS, default=1, verbose_name='单据状态')




