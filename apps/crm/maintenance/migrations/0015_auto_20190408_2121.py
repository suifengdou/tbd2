# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-04-08 21:21
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('maintenance', '0014_auto_20190408_2119'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='maintenancehandlinginfo',
            table='maintenancehandlinginfo',
        ),
        migrations.AlterModelTable(
            name='maintenanceinfo',
            table='maintenanceinfo',
        ),
        migrations.AlterModelTable(
            name='maintenancesummary',
            table='maintenancesummary',
        ),
    ]