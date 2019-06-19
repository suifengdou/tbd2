# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-06-18 19:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('machine', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goodsinfo',
            name='good_id',
            field=models.CharField(db_index=True, max_length=30, unique=True, verbose_name='货品编码'),
        ),
        migrations.AlterField(
            model_name='goodsinfo',
            name='good_name',
            field=models.CharField(db_index=True, max_length=60, unique=True, verbose_name='货品名称'),
        ),
        migrations.AlterIndexTogether(
            name='goodsinfo',
            index_together=set([]),
        ),
    ]
