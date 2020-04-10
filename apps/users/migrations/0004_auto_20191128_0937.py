# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-11-28 09:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20191128_0936'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='platform',
            field=models.SmallIntegerField(choices=[(0, '无'), (1, '淘系'), (2, '京东'), (3, '官方商城'), (4, '售后')], default=0, verbose_name='平台'),
        ),
    ]