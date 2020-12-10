# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-11-27 10:04
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('company', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('creator', models.CharField(default='system', max_length=30, verbose_name='创建者')),
                ('express_id', models.CharField(max_length=100, unique=True, verbose_name='源单号')),
                ('information', models.TextField(max_length=600, verbose_name='初始问题信息')),
                ('submit_time', models.DateTimeField(blank=True, null=True, verbose_name='客服提交时间')),
                ('servicer', models.CharField(blank=True, max_length=60, null=True, verbose_name='客服')),
                ('services_interval', models.IntegerField(blank=True, null=True, verbose_name='客服处理间隔(分钟)')),
                ('handler', models.CharField(blank=True, max_length=30, null=True, verbose_name='快递处理人')),
                ('handle_time', models.DateTimeField(blank=True, null=True, verbose_name='快递处理时间')),
                ('express_interval', models.IntegerField(blank=True, null=True, verbose_name='快递处理间隔(分钟)')),
                ('feedback', models.TextField(blank=True, max_length=900, null=True, verbose_name='反馈内容')),
                ('is_losing', models.SmallIntegerField(choices=[(0, '否'), (1, '是')], default=0, verbose_name='是否丢件')),
                ('return_express_id', models.CharField(blank=True, max_length=100, null=True, verbose_name='返回单号')),
                ('is_return', models.IntegerField(choices=[(0, '否'), (1, '是')], default=1, verbose_name='是否返回')),
                ('memo', models.TextField(blank=True, null=True, verbose_name='备注')),
                ('order_status', models.SmallIntegerField(choices=[(0, '已被取消'), (1, '快递未递'), (2, '逆向未理'), (3, '正向未递'), (4, '快递在理'), (5, '复核未理'), (6, '终审未理'), (7, '财务审核'), (8, '工单完结')], default=1, verbose_name='工单状态')),
                ('category', models.SmallIntegerField(choices=[(0, '截单退回'), (1, '无人收货'), (2, '客户拒签'), (3, '修改地址'), (4, '催件派送'), (5, '虚假签收'), (6, '丢件破损'), (7, '其他异常')], default=0, verbose_name='工单事项类型')),
                ('wo_category', models.SmallIntegerField(choices=[(0, '正向工单'), (1, '逆向工单')], default=0, verbose_name='工单类型')),
                ('process_tag', models.SmallIntegerField(choices=[(0, '未分类'), (1, '待截单'), (2, '签复核'), (3, '改地址'), (4, '催派查'), (5, '丢件核'), (6, '纠纷中'), (7, '其他')], default=0, verbose_name='处理标签')),
                ('mid_handler', models.SmallIntegerField(choices=[(0, '皮卡丘'), (1, '伊布'), (3, '波比克')], default=0, verbose_name='跟单小伙伴')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='company.LogisticsInfo', verbose_name='快递公司')),
            ],
            options={
                'verbose_name': 'EXT-快递工单-查询',
                'verbose_name_plural': 'EXT-快递工单-查询',
                'db_table': 'ext_workorderex',
            },
        ),
        migrations.CreateModel(
            name='WorkOrderApp',
            fields=[
            ],
            options={
                'verbose_name': 'EXT-快递工单-正向创建',
                'verbose_name_plural': 'EXT-快递工单-正向创建',
                'proxy': True,
                'indexes': [],
            },
            bases=('workorderex.workorder',),
        ),
        migrations.CreateModel(
            name='WorkOrderAppRev',
            fields=[
            ],
            options={
                'verbose_name': 'EXT-快递工单-逆向创建',
                'verbose_name_plural': 'EXT-快递工单-逆向创建',
                'proxy': True,
                'indexes': [],
            },
            bases=('workorderex.workorder',),
        ),
        migrations.CreateModel(
            name='WorkOrderFinance',
            fields=[
            ],
            options={
                'verbose_name': 'EXT-快递工单-财务审核',
                'verbose_name_plural': 'EXT-快递工单-财务审核',
                'proxy': True,
                'indexes': [],
            },
            bases=('workorderex.workorder',),
        ),
        migrations.CreateModel(
            name='WorkOrderHandle',
            fields=[
            ],
            options={
                'verbose_name': 'EXT-快递工单-客服处理',
                'verbose_name_plural': 'EXT-快递工单-客服处理',
                'proxy': True,
                'indexes': [],
            },
            bases=('workorderex.workorder',),
        ),
        migrations.CreateModel(
            name='WorkOrderHandleSto',
            fields=[
            ],
            options={
                'verbose_name': 'EXT-快递工单-供应商处理',
                'verbose_name_plural': 'EXT-快递工单-供应商处理',
                'proxy': True,
                'indexes': [],
            },
            bases=('workorderex.workorder',),
        ),
        migrations.CreateModel(
            name='WorkOrderKeshen',
            fields=[
            ],
            options={
                'verbose_name': 'EXT-快递工单-客审复核',
                'verbose_name_plural': 'EXT-快递工单-客审复核',
                'proxy': True,
                'indexes': [],
            },
            bases=('workorderex.workorder',),
        ),
        migrations.CreateModel(
            name='WorkOrderMine',
            fields=[
            ],
            options={
                'verbose_name': 'EXT-快递工单-终审确认',
                'verbose_name_plural': 'EXT-快递工单-终审确认',
                'proxy': True,
                'indexes': [],
            },
            bases=('workorderex.workorder',),
        ),
    ]
