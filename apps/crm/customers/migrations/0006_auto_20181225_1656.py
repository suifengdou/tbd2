# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-12-25 16:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0005_auto_20181225_1623'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customerinfo',
            name='address',
            field=models.CharField(max_length=300, verbose_name='地址'),
        ),
    ]