# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-10-29 13:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workorderex', '0003_workorder_process_tag'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workorder',
            name='process_tag',
            field=models.SmallIntegerField(choices=[(0, '未分类'), (1, '待截单'), (2, '催派查'), (3, '签复核'), (4, '丢件核'), (5, '纠纷中'), (6, '其他')], default=0, verbose_name='处理标签'),
        ),
    ]
