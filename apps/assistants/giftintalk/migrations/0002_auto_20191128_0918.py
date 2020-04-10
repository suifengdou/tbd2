# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-11-28 09:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('giftintalk', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='giftimportinfo',
            name='order_id',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='订单号'),
        ),
        migrations.AlterField(
            model_name='giftintalkinfo',
            name='platform',
            field=models.SmallIntegerField(choices=[(0, '无'), (1, '淘系'), (2, '京东')], default=0, verbose_name='平台'),
        ),
        migrations.AlterField(
            model_name='giftorderinfo',
            name='order_id',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='订单号'),
        ),
        migrations.AlterField(
            model_name='giftorderinfo',
            name='shop',
            field=models.SmallIntegerField(choices=[(0, '无'), (1, '小狗电器旗舰店'), (2, '小狗京东自营')], verbose_name='店铺名称'),
        ),
    ]