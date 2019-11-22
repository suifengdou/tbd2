# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-11-19 17:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('geography', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='WarehouseInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('creator', models.CharField(default='system', max_length=30, verbose_name='创建者')),
                ('warehouse_name', models.CharField(max_length=60, unique=True, verbose_name='仓库名称')),
                ('warehouse_id', models.CharField(max_length=20, unique=True, verbose_name='仓库ID')),
                ('receiver', models.CharField(blank=True, max_length=50, null=True, verbose_name='收货人')),
                ('mobile', models.CharField(blank=True, max_length=30, null=True, verbose_name='电话')),
                ('address', models.CharField(blank=True, max_length=90, null=True, verbose_name='地址')),
                ('status', models.IntegerField(choices=[(0, '运行'), (1, '停用')], default=0, verbose_name='仓库状态')),
            ],
            options={
                'verbose_name': 'BASE-仓库',
                'verbose_name_plural': 'BASE-仓库',
                'db_table': 'base_wah_warehouse',
            },
        ),
        migrations.CreateModel(
            name='WarehouseTypeInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('creator', models.CharField(default='system', max_length=30, verbose_name='创建者')),
                ('category', models.CharField(max_length=30, unique=True, verbose_name='仓库类型')),
            ],
            options={
                'verbose_name': 'BASE-仓库类型',
                'verbose_name_plural': 'BASE-仓库类型',
                'db_table': 'base_wah_category',
            },
        ),
        migrations.AddField(
            model_name='warehouseinfo',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='warehouse.WarehouseTypeInfo', verbose_name='仓库类型'),
        ),
        migrations.AddField(
            model_name='warehouseinfo',
            name='city',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='geography.CityInfo', verbose_name='城市地点'),
        ),
    ]
