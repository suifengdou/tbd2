# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-07-20 15:10
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='companyinfo',
            options={'verbose_name': 'BASE-公司', 'verbose_name_plural': 'BASE-公司'},
        ),
    ]