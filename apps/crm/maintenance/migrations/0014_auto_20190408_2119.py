# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-04-08 21:19
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('maintenance', '0013_auto_20190323_1036'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='maintenancehandlinginfo',
            table='MaintenanceHandlingInfo',
        ),
        migrations.AlterModelTable(
            name='maintenanceinfo',
            table='MaintenanceInfo',
        ),
        migrations.AlterModelTable(
            name='maintenancesummary',
            table='MaintenanceSummary',
        ),
    ]