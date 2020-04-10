# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2020-03-23 10:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0002_auto_20200205_1425'),
    ]

    operations = [
        migrations.CreateModel(
            name='MainInfo',
            fields=[
            ],
            options={
                'verbose_name': 'BASE-公司-本埠',
                'verbose_name_plural': 'BASE-公司-本埠',
                'proxy': True,
                'indexes': [],
            },
            bases=('company.companyinfo',),
        ),
        migrations.AlterField(
            model_name='companyinfo',
            name='category',
            field=models.IntegerField(choices=[(0, '小狗体系'), (1, '物流快递'), (2, '仓库存储'), (3, '生产制造'), (4, '经销代理'), (5, '本埠公司'), (6, '其他类型')], default=1, verbose_name='公司类型'),
        ),
    ]