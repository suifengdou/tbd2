# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2020-06-16 10:16
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('giftintalk', '0015_auto_20200613_1424'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='giftintalkinfo',
            name='dialog_detialjd',
        ),
        migrations.RemoveField(
            model_name='giftintalkinfo',
            name='dialog_detialtb',
        ),
    ]