# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-11-15 10:21
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tailsale', '0008_auto_20200808_1711'),
    ]

    operations = [
        migrations.CreateModel(
            name='TODeliverGoods',
            fields=[
            ],
            options={
                'verbose_name': 'EXT-尾货订单-发货查询',
                'verbose_name_plural': 'EXT-尾货订单-发货查询',
                'proxy': True,
                'indexes': [],
            },
            bases=('tailsale.togoods',),
        ),
    ]
