# -*- coding:  utf-8 -*-
# @Time    :  2019/5/11 13: 47
# @Author  :  Hann
# @Site    :
# @File    :  models.py
# @Software:  PyCharm

from django.db import models
import django.utils.timezone as timezone

from db.base_model import BaseModel
from apps.oms.machine.models import MachineInfo, PartInfo
from apps.oms.manufactory.models import ManufactoryInfo
from tbd2.settings import AUTH_USER_MODEL
from apps.utils.geography.models import CityInfo

class ProManuInfo(BaseModel):
    STATUS = (
        (0, '正常'),
        (1, '停用'),
    )
    goods_name = models.ForeignKey(MachineInfo, on_delete=models.CASCADE, verbose_name='机器名称')
    manufactory = models.ForeignKey(ManufactoryInfo, on_delete=models.CASCADE, verbose_name='工厂名字')
    status = models.IntegerField(choices=STATUS,  default=0, verbose_name='状态')


class PartToProInfo(BaseModel):
    STATUS = (
        (0, '正常'),
        (1, '停用'),
    )
    machine_name = models.ForeignKey(MachineInfo, on_delete=models.CASCADE, verbose_name='机器名称')
    part_name = models.ForeignKey(PartInfo, on_delete=models.CASCADE, verbose_name='配件名称')
    magnification = models.IntegerField(verbose_name='倍率')
    status = models.IntegerField(choices=STATUS, default=0, verbose_name='状态')
