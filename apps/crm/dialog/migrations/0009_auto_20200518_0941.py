# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2020-05-18 09:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dialog', '0008_auto_20200518_0935'),
    ]

    operations = [
        migrations.AlterField(
            model_name='oridetailjd',
            name='mistake_tag',
            field=models.SmallIntegerField(choices=[(0, '正常'), (1, '对话格式错误')], default=0, verbose_name='错误列表'),
        ),
    ]
