# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-06-24 09:56
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('machine', '0004_auto_20190619_0903'),
    ]

    operations = [
        migrations.DeleteModel(
            name='BatchFaultSummary',
        ),
        migrations.DeleteModel(
            name='FactoryFaultSummary',
        ),
        migrations.DeleteModel(
            name='FaultMachineSN',
        ),
        migrations.DeleteModel(
            name='GoodFaultSummary',
        ),
        migrations.DeleteModel(
            name='MachineOrder',
        ),
        migrations.DeleteModel(
            name='MachineSN',
        ),
    ]
