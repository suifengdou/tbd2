# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-06-24 12:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('machine', '0005_auto_20190624_0956'),
        ('manufactory', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GoodsToManufactoryInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('creator', models.CharField(default='system', max_length=30, verbose_name='创建者')),
                ('status', models.IntegerField(choices=[(0, '正常'), (1, '停用')], default=0, verbose_name='状态')),
                ('goods_name', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='machine.MachineInfo', verbose_name='机器名称')),
                ('manufactory', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manufactory.ManufactoryInfo', verbose_name='工厂名字')),
            ],
            options={
                'verbose_name': '货品与工厂对照表',
                'verbose_name_plural': '货品与工厂对照表',
                'db_table': 'base_rel_goods2manufactory',
            },
        ),
        migrations.CreateModel(
            name='PartToProductInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('creator', models.CharField(default='system', max_length=30, verbose_name='创建者')),
                ('magnification', models.IntegerField(verbose_name='倍率')),
                ('status', models.IntegerField(choices=[(0, '正常'), (1, '停用')], default=0, verbose_name='状态')),
                ('machine_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='machine.MachineInfo', verbose_name='机器名称')),
                ('part_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parts', to='machine.PartInfo', verbose_name='配件名称')),
            ],
            options={
                'verbose_name': '客供与机器对照表',
                'verbose_name_plural': '客供与机器对照表',
                'db_table': 'base_rel_part2product',
            },
        ),
    ]