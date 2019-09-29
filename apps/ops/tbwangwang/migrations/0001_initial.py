# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-09-28 15:40
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='WWDialogueListInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('creator', models.CharField(default='system', max_length=30, verbose_name='创建者')),
                ('dialogue_time', models.DateTimeField(verbose_name='聊天时间')),
                ('buyer_ww', models.CharField(max_length=60, verbose_name='买家旺旺')),
                ('cs_ww', models.CharField(max_length=60, verbose_name='客服旺旺')),
                ('category', models.IntegerField(choices=[(0, '接待'), (1, '非接待'), (2, '未回复')], default=0, verbose_name='类型')),
                ('memorandum', models.TextField(blank=True, null=True, verbose_name='备注')),
                ('status', models.IntegerField(choices=[(0, '已取消'), (1, '未处理'), (2, '已完成')], default=1, verbose_name='系统状态')),
            ],
            options={
                'verbose_name': '旺旺对话总明细',
                'verbose_name_plural': '旺旺对话总明细',
                'db_table': 'ops_ww_dialogue',
            },
        ),
        migrations.CreateModel(
            name='WWFilterationInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('creator', models.CharField(default='system', max_length=30, verbose_name='创建者')),
                ('dialogue_time', models.DateTimeField(verbose_name='聊天时间')),
                ('buyer_ww', models.CharField(max_length=60, verbose_name='买家旺旺')),
                ('start_time', models.TimeField(verbose_name='开始时间')),
                ('end_time', models.TimeField(verbose_name='结束时间')),
                ('cs_ww', models.CharField(max_length=60, verbose_name='客服旺旺')),
                ('filter_category', models.CharField(max_length=30, verbose_name='过滤类型')),
                ('status', models.IntegerField(choices=[(0, '已取消'), (1, '未处理'), (2, '已完成')], default=1, verbose_name='系统状态')),
                ('shop', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='shop.ShopInfo', verbose_name='店铺')),
            ],
            options={
                'verbose_name': '旺旺接待过滤',
                'verbose_name_plural': '旺旺接待过滤',
                'db_table': 'ops_ww_filteration',
            },
        ),
        migrations.CreateModel(
            name='WWNoReplayInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('creator', models.CharField(default='system', max_length=30, verbose_name='创建者')),
                ('dialogue_time', models.DateTimeField(verbose_name='日期')),
                ('start_time', models.TimeField(verbose_name='开始时间')),
                ('buyer_ww', models.CharField(max_length=60, verbose_name='买家旺旺')),
                ('cs_ww', models.CharField(max_length=60, verbose_name='客服旺旺')),
                ('status', models.IntegerField(choices=[(0, '已取消'), (1, '未处理'), (2, '已完成')], default=1, verbose_name='系统状态')),
            ],
            options={
                'verbose_name': '旺旺未回复',
                'verbose_name_plural': '旺旺未回复',
                'db_table': 'ops_ww_noreplay',
            },
        ),
        migrations.CreateModel(
            name='WWReceptionInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('creator', models.CharField(default='system', max_length=30, verbose_name='创建者')),
                ('dialogue_time', models.DateTimeField(verbose_name='日期')),
                ('start_time', models.TimeField(verbose_name='开始时间')),
                ('end_time', models.TimeField(verbose_name='结束时间')),
                ('buyer_ww', models.CharField(max_length=60, verbose_name='买家旺旺')),
                ('cs_ww', models.CharField(max_length=60, verbose_name='客服旺旺')),
                ('category', models.CharField(max_length=30, verbose_name='接待类型')),
                ('initiator', models.CharField(max_length=30, verbose_name='接待发起')),
                ('order_status', models.CharField(max_length=30, verbose_name='状态')),
                ('status', models.IntegerField(choices=[(0, '已取消'), (1, '未处理'), (2, '已完成')], default=1, verbose_name='系统状态')),
            ],
            options={
                'verbose_name': '旺旺接待记录',
                'verbose_name_plural': '旺旺接待记录',
                'db_table': 'ops_ww_reception',
            },
        ),
    ]
