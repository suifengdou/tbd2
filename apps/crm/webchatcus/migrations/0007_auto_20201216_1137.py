# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-12-16 11:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webchatcus', '0006_remove_oriwarrantyinfo_birthday'),
    ]

    operations = [
        migrations.AlterField(
            model_name='oriwarrantyinfo',
            name='smartphone',
            field=models.CharField(blank=True, max_length=60, null=True, verbose_name='手机号'),
        ),
    ]
