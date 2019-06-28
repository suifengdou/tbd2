# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-06-18 17:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CityInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('creator', models.CharField(default='system', max_length=30, verbose_name='创建者')),
                ('city', models.CharField(max_length=100, unique=True, verbose_name='城市')),
                ('area_code', models.CharField(max_length=10, verbose_name='电话区号')),
            ],
            options={
                'verbose_name': '城市',
                'verbose_name_plural': '城市',
                'db_table': 'util_geo_city',
            },
        ),
        migrations.CreateModel(
            name='NationalityInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('creator', models.CharField(default='system', max_length=30, verbose_name='创建者')),
                ('nationality', models.CharField(max_length=100, unique=True, verbose_name='国家及地区')),
                ('abbreviation', models.CharField(max_length=3, unique=True, verbose_name='缩写')),
                ('area_code', models.CharField(max_length=10, unique=True, verbose_name='电话区号')),
            ],
            options={
                'verbose_name': '国家及地区',
                'verbose_name_plural': '国家及地区',
                'db_table': 'util_geo_nationality',
            },
        ),
        migrations.CreateModel(
            name='ProvinceInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('creator', models.CharField(default='system', max_length=30, verbose_name='创建者')),
                ('province', models.CharField(max_length=150, unique=True, verbose_name='省份')),
                ('area_code', models.CharField(max_length=10, unique=True, verbose_name='电话区号')),
                ('nationality', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='geography.NationalityInfo', verbose_name='国家')),
            ],
            options={
                'verbose_name': '省份',
                'verbose_name_plural': '省份',
                'db_table': 'util_geo_province',
            },
        ),
        migrations.AddField(
            model_name='cityinfo',
            name='nationality',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='geography.NationalityInfo', verbose_name='国家'),
        ),
        migrations.AddField(
            model_name='cityinfo',
            name='province',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='geography.ProvinceInfo', verbose_name='省份'),
        ),
    ]