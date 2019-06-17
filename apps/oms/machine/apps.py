# -*- coding: utf-8 -*-
# @Time    : 2019/5/13 10:41
# @Author  : Hann
# @Site    :
# @File    : apps.py
# @Software: PyCharm

from django.apps import AppConfig


class MachineConfig(AppConfig):
    # 名字要带路径
    name = 'apps.oms.machine'
    verbose_name = 'oms-machine'
