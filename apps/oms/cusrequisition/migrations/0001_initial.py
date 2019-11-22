# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-11-19 17:38
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
            name='CusRequisitionInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('creator', models.CharField(default='system', max_length=30, verbose_name='创建者')),
                ('planorder_id', models.CharField(db_index=True, max_length=30, verbose_name='计划采购单号')),
                ('batch_num', models.CharField(db_index=True, max_length=30, verbose_name='批次号')),
                ('goods_id', models.CharField(max_length=30, verbose_name='货品编码')),
                ('goods_name', models.CharField(max_length=60, verbose_name='货品名称')),
                ('quantity', models.IntegerField(verbose_name='货品数量')),
                ('estimated_time', models.DateTimeField(verbose_name='期望到货时间')),
                ('order_status', models.IntegerField(choices=[(0, '已取消'), (1, '未处理'), (2, '已递交'), (3, '异常')], default=1, verbose_name='需求单单状态')),
                ('cus_requisition_id', models.CharField(blank=True, max_length=30, null=True, unique=True, verbose_name='需求单号')),
                ('manufactory', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='company.ManuInfo', verbose_name='工厂名称')),
            ],
            options={
                'verbose_name': 'OMS-R-需求单',
                'verbose_name_plural': 'OMS-R-需求单',
                'db_table': 'oms_cr_requisition',
            },
        ),
        migrations.CreateModel(
            name='CusRequisitionSubmitInfo',
            fields=[
            ],
            options={
                'verbose_name': 'OMS-R-未递交需求单',
                'verbose_name_plural': 'OMS-R-未递交需求单',
                'proxy': True,
                'indexes': [],
            },
            bases=('cusrequisition.cusrequisitioninfo',),
        ),
    ]
