# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2020-02-21 16:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20191128_0937'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='platform',
            field=models.SmallIntegerField(choices=[(0, '无'), (1, '淘系'), (2, '非淘'), (3, '官方商城'), (4, '售后')], default=0, verbose_name='平台'),
        ),
    ]
