# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-12-30 16:19
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('manuorder', '0002_manuorderinfo_tag_sign'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='manuorderpenddinginfo',
            options={'verbose_name': 'OMS-M-待审核生产列表', 'verbose_name_plural': 'OMS-M-待审核生产列表'},
        ),
    ]
