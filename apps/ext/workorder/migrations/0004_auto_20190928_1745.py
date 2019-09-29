# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-09-28 17:45
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('workorder', '0003_auto_20190928_1733'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workorder',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='company.LogisticsInfo', verbose_name='快递公司'),
        ),
    ]
