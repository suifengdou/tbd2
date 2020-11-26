# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-11-24 16:57
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('customers', '0005_auto_20201121_1337'),
    ]

    operations = [
        migrations.CreateModel(
            name='LabelDetial',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('creator', models.CharField(default='system', max_length=30, verbose_name='创建者')),
                ('order_status', models.SmallIntegerField(choices=[(0, '已取消'), (1, '待关联'), (2, '已完成')], db_index=True, default=1, verbose_name='单据状态')),
                ('mistake_tag', models.SmallIntegerField(choices=[(0, '正常'), (1, '已存在标记，不可重复标记')], default=0, verbose_name='错误列表')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customers.CustomerInfo', verbose_name='客户')),
            ],
            options={
                'verbose_name': 'CRM-标签关联单-明细',
                'verbose_name_plural': 'CRM-标签关联单-明细',
                'db_table': 'crm_label_orderdetail',
            },
        ),
        migrations.CreateModel(
            name='LabelInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('creator', models.CharField(default='system', max_length=30, verbose_name='创建者')),
                ('name', models.CharField(db_index=True, max_length=120, unique=True, verbose_name='标签名称')),
                ('order_category', models.SmallIntegerField(choices=[(1, '常规类型'), (2, '特殊类型'), (3, '自动创建')], db_index=True, default=1, verbose_name='标签类型')),
                ('memorandum', models.CharField(max_length=220, verbose_name='标签说明')),
                ('order_status', models.SmallIntegerField(choices=[(0, '已取消'), (1, '正常')], db_index=True, default=1, verbose_name='单据状态')),
            ],
            options={
                'verbose_name': 'CRM-标签-标签管理',
                'verbose_name_plural': 'CRM-标签-标签管理',
                'db_table': 'crm_label_label',
            },
        ),
        migrations.CreateModel(
            name='LabelOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('creator', models.CharField(default='system', max_length=30, verbose_name='创建者')),
                ('order_id', models.CharField(max_length=150, unique=True, verbose_name='单据编号')),
                ('quantity', models.IntegerField(verbose_name='客户数量')),
                ('order_status', models.SmallIntegerField(choices=[(0, '已取消'), (1, '未关联'), (2, '已完成')], db_index=True, default=1, verbose_name='单据状态')),
                ('label', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cslabel.LabelInfo', verbose_name='标签')),
            ],
            options={
                'verbose_name': 'CRM-标签关联单-查询',
                'verbose_name_plural': 'CRM-标签关联单-查询',
                'db_table': 'crm_label_order',
            },
        ),
        migrations.AddField(
            model_name='labeldetial',
            name='label',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cslabel.LabelInfo', verbose_name='标签'),
        ),
        migrations.AddField(
            model_name='labeldetial',
            name='label_order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cslabel.LabelOrder', verbose_name='标签关联单'),
        ),
        migrations.CreateModel(
            name='AssociateLabel',
            fields=[
            ],
            options={
                'verbose_name': 'CRM-标签关联单-待关联',
                'verbose_name_plural': 'CRM-标签关联单-待关联',
                'proxy': True,
                'indexes': [],
            },
            bases=('cslabel.labelorder',),
        ),
        migrations.AlterUniqueTogether(
            name='labeldetial',
            unique_together=set([('label', 'customer')]),
        ),
    ]
