# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2020-06-13 10:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workorderguarantee', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='WOFinish',
        ),
        migrations.CreateModel(
            name='WOPFinish',
            fields=[
            ],
            options={
                'verbose_name': 'EXT-技术工单-客服终审',
                'verbose_name_plural': 'EXT-技术工单-客服终审',
                'proxy': True,
                'indexes': [],
            },
            bases=('workorderguarantee.workorder',),
        ),
        migrations.CreateModel(
            name='WORFinish',
            fields=[
            ],
            options={
                'verbose_name': 'EXT-技术工单-技术终审',
                'verbose_name_plural': 'EXT-技术工单-技术终审',
                'proxy': True,
                'indexes': [],
            },
            bases=('workorderguarantee.workorder',),
        ),
        migrations.AlterField(
            model_name='workorder',
            name='express_id',
            field=models.CharField(db_index=True, max_length=100, unique=True, verbose_name='快递单号'),
        ),
        migrations.AlterField(
            model_name='workorder',
            name='mistake_tag',
            field=models.SmallIntegerField(choices=[(0, '正常'), (1, '物流单号错误'), (2, '单据类型错误'), (3, '反馈信息为空'), (4, '驳回')], default=0, verbose_name='异常原因'),
        ),
        migrations.AlterField(
            model_name='workorder',
            name='order_status',
            field=models.SmallIntegerField(choices=[(0, '已被取消'), (1, '未递交'), (2, '工单在理'), (3, '终审未理'), (4, '工单完结')], default=1, verbose_name='工单状态'),
        ),
        migrations.AlterField(
            model_name='workorder',
            name='wo_category',
            field=models.SmallIntegerField(choices=[(0, '正向工单'), (1, '逆向工单')], default=1, verbose_name='工单类型'),
        ),
    ]
