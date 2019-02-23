# -*- coding: utf-8 -*-
# @Time    : 2018/11/25 16:23
# @Author  : Hann
# @Site    : 
# @File    : base_model.py.py
# @Software: PyCharm

from django.db import models


class BaseModel(models.Model):
    """模型抽象基类"""
    create_time = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name=u'更新时间')
    is_delete = models.BooleanField(default=False, verbose_name=u'删除标记')
    creator = models.CharField(max_length=30, default='system', verbose_name='创建者')

    class Meta:
        abstract = True