# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-11-25 17:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0005_auto_20201121_1337'),
        ('cslabel', '0004_auto_20201125_1447'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssociateLabelDetial',
            fields=[
            ],
            options={
                'verbose_name': 'CRM-标签关联明细单-待关联',
                'verbose_name_plural': 'CRM-标签关联明细单-待关联',
                'proxy': True,
                'indexes': [],
            },
            bases=('cslabel.labeldetial',),
        ),
        migrations.AlterModelOptions(
            name='labeldetial',
            options={'verbose_name': 'CRM-标签关联明细单-查询', 'verbose_name_plural': 'CRM-标签关联明细单-查询'},
        ),
        migrations.AddField(
            model_name='labelorder',
            name='service_num',
            field=models.IntegerField(default=0, verbose_name='关联任务次数'),
        ),
        migrations.AlterUniqueTogether(
            name='labeldetial',
            unique_together=set([('label_order', 'customer')]),
        ),
    ]
