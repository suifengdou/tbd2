# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-06-26 19:48
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('relationship', '0004_manufactorytowarehouse'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='manufactorytowarehouse',
            options={'verbose_name': '客供与机器对照表', 'verbose_name_plural': '客供与机器对照表'},
        ),
        migrations.AlterModelTable(
            name='manufactorytowarehouse',
            table='base_rel_manu2wh',
        ),
    ]