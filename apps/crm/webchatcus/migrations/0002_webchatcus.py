# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-12-15 11:14
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0001_initial'),
        ('webchatcus', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='WebchatCus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('creator', models.CharField(default='system', max_length=30, verbose_name='创建者')),
                ('order_status', models.SmallIntegerField(choices=[(0, '已取消'), (1, '未处理'), (2, '已完成')], db_index=True, default=1, verbose_name='单据状态')),
                ('customer', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='customers.CustomerInfo', verbose_name='客户')),
            ],
            options={
                'verbose_name': 'crm-微信公众号客户列表-查询',
                'verbose_name_plural': 'crm-微信公众号客户列表-查询',
                'db_table': 'crm_webchart_customers',
            },
        ),
    ]
