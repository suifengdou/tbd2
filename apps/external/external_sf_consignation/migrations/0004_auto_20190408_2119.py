# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-04-08 21:19
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('external_sf_consignation', '0003_sfconsignation_creator'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='sfconsignation',
            table='sfconsignation',
        ),
    ]