# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-04-22 12:47
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('machine', '0003_auto_20190422_1025'),
    ]

    operations = [
        migrations.RenameField(
            model_name='machineorder',
            old_name='msn',
            new_name='msn_segment',
        ),
        migrations.RemoveField(
            model_name='machineorder',
            name='tosum_status',
        ),
    ]
