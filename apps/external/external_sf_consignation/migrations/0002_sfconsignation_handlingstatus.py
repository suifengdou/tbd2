# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-12-16 17:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('external_sf_consignation', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sfconsignation',
            name='handlingstatus',
            field=models.CharField(choices=[(0, '未审核'), (1, '已处理'), (2, '已完结')], default=0, max_length=30, verbose_name='委托单状态'),
        ),
    ]
