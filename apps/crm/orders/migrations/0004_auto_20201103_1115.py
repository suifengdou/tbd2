# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2020-11-03 11:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_auto_20201103_1022'),
    ]

    operations = [
        migrations.AlterField(
            model_name='oriorderinfo',
            name='order_category',
            field=models.CharField(db_index=True, max_length=40, verbose_name='订单类型'),
        ),
    ]