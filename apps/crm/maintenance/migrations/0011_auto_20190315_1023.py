# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-03-15 10:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maintenance', '0010_auto_20190312_1657'),
    ]

    operations = [
        migrations.AlterField(
            model_name='maintenancesummary',
            name='finish_date',
            field=models.DateTimeField(verbose_name='保修完成日期'),
        ),
    ]