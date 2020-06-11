# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2020-06-10 09:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workorderinvoice', '0029_auto_20200518_0935'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoiceorder',
            name='account',
            field=models.CharField(blank=True, max_length=60, null=True, verbose_name='银行账号'),
        ),
        migrations.AlterField(
            model_name='workorder',
            name='account',
            field=models.CharField(blank=True, max_length=60, null=True, verbose_name='银行账号'),
        ),
    ]
