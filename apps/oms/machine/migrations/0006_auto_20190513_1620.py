# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-05-13 16:20
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('machine', '0005_auto_20190513_1457'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='machineinfo',
            index_together=set([('machine_name', 'machine_id')]),
        ),
    ]