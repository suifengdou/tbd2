# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-01-09 16:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0010_auto_20190109_1349'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customerinfo',
            name='name',
            field=models.CharField(max_length=100, verbose_name='姓名'),
        ),
    ]
