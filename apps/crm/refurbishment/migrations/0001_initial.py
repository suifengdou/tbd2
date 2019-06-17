# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-06-06 12:35
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ApprasialInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('creator', models.CharField(default='system', max_length=30, verbose_name='创建者')),
                ('appraisal', models.CharField(max_length=30, unique=True, verbose_name='故障判断')),
            ],
            options={
                'verbose_name': '故障列表',
                'verbose_name_plural': '故障列表',
                'db_table': 'crm_ref_appraisalinfo',
            },
        ),
        migrations.CreateModel(
            name='OriRefurbishInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('creator', models.CharField(default='system', max_length=30, verbose_name='创建者')),
                ('ref_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='翻新时间')),
                ('pre_sn', models.CharField(max_length=20, verbose_name='序列号前缀')),
                ('mid_batch', models.CharField(choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')], default='A', max_length=1, verbose_name='中间批次识别')),
                ('tail_sn', models.CharField(max_length=5, null=True, verbose_name='尾号')),
                ('submit_tag', models.IntegerField(choices=[(0, '未递交'), (1, '已处理'), (2, '重复订单'), (3, '异常')], default=0, verbose_name='生成状态')),
                ('new_sn', models.CharField(blank=True, max_length=30, null=True, verbose_name='新序列号')),
                ('appraisal', models.ForeignKey(default=39, on_delete=django.db.models.deletion.CASCADE, to='refurbishment.ApprasialInfo', verbose_name='故障判断')),
            ],
            options={
                'verbose_name': '原始翻新列表',
                'verbose_name_plural': '原始翻新列表',
                'db_table': 'crm_ref_orirefurbinshinfo',
            },
        ),
        migrations.CreateModel(
            name='RefurbishGoodSummary',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('creator', models.CharField(default='system', max_length=30, verbose_name='创建者')),
                ('statistical_time', models.DateTimeField(verbose_name='统计时间')),
                ('goods_name', models.CharField(max_length=60, verbose_name='机器名称')),
                ('goods_id', models.CharField(max_length=30, verbose_name='机器编码')),
                ('quantity', models.IntegerField(verbose_name='翻新数量')),
                ('submit_tag', models.IntegerField(choices=[(0, '未递交'), (1, '已处理'), (2, '已出库'), (3, '异常')], default=0, verbose_name='生成状态')),
            ],
            options={
                'verbose_name': '翻新机器统计列表',
                'verbose_name_plural': '翻新机器统计列表',
                'db_table': 'crm_ref_refurbishgoodsummary',
            },
        ),
        migrations.CreateModel(
            name='RefurbishInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('creator', models.CharField(default='system', max_length=30, verbose_name='创建者')),
                ('ref_time', models.DateTimeField(verbose_name='翻新时间')),
                ('goods_name', models.CharField(max_length=60, verbose_name='机器名称')),
                ('goods_id', models.CharField(max_length=30, verbose_name='机器编码')),
                ('appraisal', models.CharField(max_length=60, verbose_name='故障判断')),
                ('m_sn', models.CharField(max_length=30, verbose_name='机器序列号')),
                ('technician', models.CharField(max_length=30, verbose_name='技术员')),
                ('memo', models.CharField(blank=True, max_length=60, null=True, verbose_name='备注信息')),
                ('submit_tag', models.IntegerField(choices=[(0, '未递交'), (1, '已处理'), (2, '售后质量'), (3, '异常')], default=0, verbose_name='生成状态')),
                ('summary_tag', models.IntegerField(choices=[(0, '未递交'), (1, '已处理'), (2, '售后质量'), (3, '异常')], default=0, verbose_name='生成状态')),
            ],
            options={
                'verbose_name': '翻新列表',
                'verbose_name_plural': '翻新列表',
                'db_table': 'crm_ref_refurbinshinfo',
            },
        ),
        migrations.CreateModel(
            name='RefurbishTechSummary',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('creator', models.CharField(default='system', max_length=30, verbose_name='创建者')),
                ('statistical_time', models.DateTimeField(verbose_name='统计时间')),
                ('technician', models.CharField(max_length=30, verbose_name='技术员')),
                ('quantity', models.IntegerField(verbose_name='翻新数量')),
            ],
            options={
                'verbose_name': '技术员翻新统计列表',
                'verbose_name_plural': '技术员翻新统计列表',
                'db_table': 'crm_ref_refurbishtechsummary',
            },
        ),
    ]
