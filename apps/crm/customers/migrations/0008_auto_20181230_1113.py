# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-12-30 11:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0007_auto_20181226_1446'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customerinfo',
            name='gift_times',
            field=models.IntegerField(default=0, verbose_name='赠品次数'),
        ),
    ]
