from django.db import models

# Create your models here.
# -*- coding: utf-8 -*-
# @Time    : 2019/4/14 20:58
# @Author  : Hann
# @Site    :
# @File    : models.py
# @Software: PyCharm


from django.db import models

from db.base_model import BaseModel


class DepartmentInfo(BaseModel):

    name = models.CharField(max_length=50, unique=True, verbose_name='部门名称')
    d_id = models.CharField(max_length=50, unique=True, verbose_name='部门ID')

    class Meta:
        verbose_name = 'BASE-部门-部门管理'
        verbose_name_plural = verbose_name
        db_table = 'base_department'

    def __str__(self):
        return self.name

