# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-04-20 13:43
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0016_auto_20190410_1701'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='orderinfo',
            table='crm_o_orderinfo',
        ),
        migrations.AlterModelTable(
            name='oriorderinfo',
            table='crm_o_oriorderinfo',
        ),
    ]