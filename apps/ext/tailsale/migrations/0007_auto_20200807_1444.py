# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2020-08-07 14:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tailsale', '0006_auto_20200806_1641'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tailpartsorder',
            name='message',
            field=models.TextField(blank=True, null=True, verbose_name='备注'),
        ),
    ]