# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-05-09 15:40
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('maintenance', '0022_maintenancehandlinginfo_reason_analysis'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='maintenancehandlinginfo',
            name='reason_analysis',
        ),
    ]
