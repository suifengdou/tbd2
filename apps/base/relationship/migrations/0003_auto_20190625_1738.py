# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-06-25 17:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('relationship', '0002_goodstomanufactoryinfo_category'),
    ]

    operations = [
        migrations.CreateModel(
            name='CusPartToManufactoryInfo',
            fields=[
            ],
            options={
                'verbose_name': '客供件工厂对照表',
                'verbose_name_plural': '客供件工厂对照表',
                'proxy': True,
                'indexes': [],
            },
            bases=('relationship.goodstomanufactoryinfo',),
        ),
        migrations.CreateModel(
            name='MachineToManufactoryInfo',
            fields=[
            ],
            options={
                'verbose_name': '整机工厂对照表',
                'verbose_name_plural': '整机工厂对照表',
                'proxy': True,
                'indexes': [],
            },
            bases=('relationship.goodstomanufactoryinfo',),
        ),
        migrations.CreateModel(
            name='PartToManufactoryInfo',
            fields=[
            ],
            options={
                'verbose_name': '配件工厂对照表',
                'verbose_name_plural': '配件工厂对照表',
                'proxy': True,
                'indexes': [],
            },
            bases=('relationship.goodstomanufactoryinfo',),
        ),
        migrations.AlterField(
            model_name='goodstomanufactoryinfo',
            name='goods_name',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='machine.GoodsInfo', verbose_name='机器名称'),
        ),
    ]