# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2020-04-13 17:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workorderinvoice', '0021_invoicegoods_goods_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoiceorder',
            name='nickname',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='客户昵称'),
        ),
        migrations.AddField(
            model_name='workorder',
            name='nickname',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='客户昵称'),
        ),
    ]
