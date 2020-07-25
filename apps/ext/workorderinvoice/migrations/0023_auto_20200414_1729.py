# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2020-04-14 17:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workorderinvoice', '0022_auto_20200413_1744'),
    ]

    operations = [
        migrations.AddField(
            model_name='deliverorder',
            name='remark',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='买家备注'),
        ),
        migrations.AlterField(
            model_name='deliverorder',
            name='message',
            field=models.CharField(max_length=150, verbose_name='客服备注'),
        ),
    ]