# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-06-27 13:30
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0007_remove_stockinfo_source_order_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockinorderinfo',
            name='warehouse',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='warehouse.WarehouseInfo', verbose_name='仓库名称'),
        ),
        migrations.AlterField(
            model_name='stockoutinfo',
            name='category',
            field=models.IntegerField(choices=[(0, '常规出库'), (1, '客供出库'), (2, '配件出库')], default=0, verbose_name='出库类型'),
        ),
        migrations.AlterField(
            model_name='stockoutinfo',
            name='warehouse',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='warehouse.WarehouseInfo', verbose_name='仓库名称'),
        ),
    ]
