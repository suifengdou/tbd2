# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-04-20 13:14
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('maintenance', '0019_auto_20190410_2050'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='maintenancehandlinginfo',
            table='crm_m_maintenancehandlinginfo',
        ),
        migrations.AlterModelTable(
            name='maintenanceinfo',
            table='crm_m_maintenanceinfo',
        ),
        migrations.AlterModelTable(
            name='maintenancesummary',
            table='crm_m_maintenancesummary',
        ),
    ]
