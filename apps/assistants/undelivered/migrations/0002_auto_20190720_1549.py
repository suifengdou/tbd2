# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-07-20 15:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('undelivered', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='oriorderinfo',
            name='status',
            field=models.IntegerField(choices=[(0, '等待处理'), (1, '无需处理'), (2, '特别跟进'), (3, '暂不处理'), (4, '半退未发'), (5, '未发订金')], default=0, verbose_name='单据处理状态'),
        ),
    ]
