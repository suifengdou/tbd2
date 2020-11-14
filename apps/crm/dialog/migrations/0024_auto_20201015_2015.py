# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2020-10-15 20:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dialog', '0023_auto_20201015_1930'),
    ]

    operations = [
        migrations.AlterField(
            model_name='oridetailjd',
            name='extract_tag',
            field=models.SmallIntegerField(choices=[(0, '否'), (1, '是')], db_index=True, default=0, verbose_name='是否提取订单'),
        ),
        migrations.AlterField(
            model_name='oridetailjd',
            name='order_status',
            field=models.SmallIntegerField(choices=[(0, '被取消'), (1, '未过滤'), (2, '未质检')], db_index=True, default=1, verbose_name='单据状态'),
        ),
        migrations.AlterField(
            model_name='oridetailow',
            name='extract_tag',
            field=models.SmallIntegerField(choices=[(0, '否'), (1, '是')], db_index=True, default=0, verbose_name='是否提取订单'),
        ),
        migrations.AlterField(
            model_name='oridetailow',
            name='order_status',
            field=models.SmallIntegerField(choices=[(0, '被取消'), (1, '正常')], db_index=True, default=1, verbose_name='单据状态'),
        ),
        migrations.AlterField(
            model_name='oridetailtb',
            name='extract_tag',
            field=models.SmallIntegerField(choices=[(0, '否'), (1, '是')], db_index=True, default=0, verbose_name='是否提取订单'),
        ),
        migrations.AlterField(
            model_name='oridetailtb',
            name='order_status',
            field=models.SmallIntegerField(choices=[(0, '被取消'), (1, '正常')], db_index=True, default=1, verbose_name='单据状态'),
        ),
    ]