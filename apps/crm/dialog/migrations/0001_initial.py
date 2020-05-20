# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2020-05-07 17:41
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DialogTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('creator', models.CharField(default='system', max_length=30, verbose_name='创建者')),
                ('name', models.CharField(max_length=30, verbose_name='标签名')),
                ('category', models.SmallIntegerField(choices=[(0, '无法定义'), (1, '售前'), (2, '售后')], default=0, verbose_name='标签类型')),
                ('order_status', models.SmallIntegerField(choices=[(0, '被取消'), (1, '正常')], default=1, verbose_name='单据状态')),
            ],
            options={
                'verbose_name': 'CRM-对话-标签',
                'verbose_name_plural': 'CRM-对话-标签',
                'db_table': 'crm_dialog_tag',
            },
        ),
        migrations.CreateModel(
            name='OriDetailJD',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('creator', models.CharField(default='system', max_length=30, verbose_name='创建者')),
                ('sayer', models.CharField(db_index=True, max_length=150, verbose_name='讲话者')),
                ('status', models.SmallIntegerField(choices=[(0, '客服'), (1, '顾客')], verbose_name='角色')),
                ('time', models.DateTimeField(db_index=True, verbose_name='时间')),
                ('interval', models.IntegerField(verbose_name='对话间隔(秒)')),
                ('content', models.TextField(verbose_name='内容')),
                ('order_status', models.SmallIntegerField(choices=[(0, '被取消'), (1, '正常')], default=1, verbose_name='单据状态')),
            ],
            options={
                'verbose_name': 'CRM-京东对话信息-查询',
                'verbose_name_plural': 'CRM-京东对话信息-查询',
                'db_table': 'crm_diadetail_orijingdong',
            },
        ),
        migrations.CreateModel(
            name='OriDetailTB',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('creator', models.CharField(default='system', max_length=30, verbose_name='创建者')),
                ('sayer', models.CharField(db_index=True, max_length=150, verbose_name='讲话者')),
                ('status', models.SmallIntegerField(choices=[(0, '客服'), (1, '顾客')], verbose_name='角色')),
                ('time', models.DateTimeField(db_index=True, verbose_name='时间')),
                ('interval', models.IntegerField(verbose_name='对话间隔(秒)')),
                ('content', models.TextField(verbose_name='内容')),
                ('order_status', models.SmallIntegerField(choices=[(0, '被取消'), (1, '正常')], default=1, verbose_name='单据状态')),
            ],
            options={
                'verbose_name': 'CRM-淘系对话信息-查询',
                'verbose_name_plural': 'CRM-淘系对话信息-查询',
                'db_table': 'crm_diadetail_oritaobao',
            },
        ),
        migrations.CreateModel(
            name='OriDialogJD',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('creator', models.CharField(default='system', max_length=30, verbose_name='创建者')),
                ('shop', models.CharField(db_index=True, max_length=60, verbose_name='店铺')),
                ('customer', models.CharField(db_index=True, max_length=150, unique=True, verbose_name='客户')),
                ('start_time', models.DateTimeField(verbose_name='开始时间')),
                ('end_time', models.DateTimeField(verbose_name='结束时间')),
                ('min', models.IntegerField(verbose_name='总人次')),
                ('order_status', models.SmallIntegerField(choices=[(0, '被取消'), (1, '正常')], default=1, verbose_name='单据状态')),
                ('dialog_tag', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dialog.DialogTag', verbose_name='对话标签')),
            ],
            options={
                'verbose_name': 'CRM-京东对话客户-查询',
                'verbose_name_plural': 'CRM-京东对话客户-查询',
                'db_table': 'crm_dialog_orijingdong',
            },
        ),
        migrations.CreateModel(
            name='OriDialogTB',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('creator', models.CharField(default='system', max_length=30, verbose_name='创建者')),
                ('shop', models.CharField(db_index=True, max_length=60, verbose_name='店铺')),
                ('customer', models.CharField(db_index=True, max_length=150, unique=True, verbose_name='客户')),
                ('start_time', models.DateTimeField(verbose_name='开始时间')),
                ('end_time', models.DateTimeField(verbose_name='结束时间')),
                ('min', models.IntegerField(verbose_name='总人次')),
                ('order_status', models.SmallIntegerField(choices=[(0, '被取消'), (1, '正常')], default=1, verbose_name='单据状态')),
                ('dialog_tag', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dialog.DialogTag', verbose_name='对话标签')),
            ],
            options={
                'verbose_name': 'CRM-淘系对话客户-查询',
                'verbose_name_plural': 'CRM-淘系对话客户-查询',
                'db_table': 'crm_dialog_oritaobao',
            },
        ),
        migrations.AddField(
            model_name='oridetailtb',
            name='dialog_tb',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dialog.OriDialogTB', verbose_name='对话'),
        ),
        migrations.AddField(
            model_name='oridetailjd',
            name='dialog_jd',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dialog.OriDialogJD', verbose_name='对话'),
        ),
    ]
