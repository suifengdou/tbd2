# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-12-15 11:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('customers', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OriWarrantyInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('creator', models.CharField(default='system', max_length=30, verbose_name='创建者')),
                ('warranty_sn', models.CharField(max_length=150, unique=True, verbose_name='延保码')),
                ('batch_name', models.CharField(max_length=150, verbose_name='所属批次')),
                ('duration', models.IntegerField(verbose_name='延保时长')),
                ('goods_name', models.CharField(max_length=150, verbose_name='商品型号')),
                ('produce_sn', models.CharField(max_length=150, verbose_name='序列号')),
                ('purchase_time', models.DateTimeField(verbose_name='购买时间')),
                ('register_time', models.DateTimeField(blank=True, null=True, verbose_name='产品注册时间')),
                ('webchat_name', models.CharField(blank=True, max_length=150, null=True, verbose_name='微信昵称')),
                ('name', models.CharField(blank=True, max_length=150, null=True, verbose_name='姓名')),
                ('birthday', models.DateTimeField(blank=True, null=True, verbose_name='生日')),
                ('gender', models.CharField(max_length=10, verbose_name='性别')),
                ('smartphone', models.CharField(blank=True, max_length=10, null=True, verbose_name='手机号')),
                ('area', models.CharField(blank=True, max_length=150, null=True, verbose_name='真实区域')),
                ('living_area', models.CharField(blank=True, max_length=60, null=True, verbose_name='家庭面积')),
                ('family', models.CharField(blank=True, max_length=150, null=True, verbose_name='家庭成员')),
                ('habit', models.CharField(blank=True, max_length=150, null=True, verbose_name='兴趣爱好')),
                ('other_habit', models.CharField(blank=True, max_length=150, null=True, verbose_name='其他兴趣')),
                ('order_status', models.SmallIntegerField(choices=[(0, '已取消'), (1, '未处理'), (2, '已完成')], db_index=True, default=1, verbose_name='单据状态')),
                ('process_tag', models.SmallIntegerField(choices=[(0, '未处理'), (1, '待核实'), (2, '已确认'), (3, '待清理'), (4, '已处理'), (5, '驳回'), (6, '特殊订单')], default=0, verbose_name='处理标签')),
                ('mistake_tag', models.SmallIntegerField(choices=[(0, '正常'), (1, '已导入过的订单'), (2, '待确认重复订单')], default=0, verbose_name='错误列表')),
            ],
            options={
                'verbose_name': 'crm-微信公众号原始延保码-查询',
                'verbose_name_plural': 'crm-微信公众号原始延保码-查询',
                'db_table': 'crm_webchart_oriwarranty',
            },
        ),
        migrations.CreateModel(
            name='OriWebchatInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('creator', models.CharField(default='system', max_length=30, verbose_name='创建者')),
                ('type', models.CharField(max_length=60, verbose_name='机器类别')),
                ('goods_code', models.CharField(max_length=60, verbose_name='产品ID')),
                ('goods_name', models.CharField(max_length=150, verbose_name='产品名称')),
                ('goods_series', models.CharField(max_length=60, verbose_name='货品序号')),
                ('goods_id', models.CharField(max_length=150, verbose_name='型号')),
                ('produce_year', models.CharField(blank=True, max_length=60, null=True, verbose_name='生产年')),
                ('produce_week', models.CharField(blank=True, max_length=60, null=True, verbose_name='生产周')),
                ('produce_batch', models.CharField(blank=True, max_length=60, null=True, verbose_name='周批次')),
                ('produce_sn', models.CharField(blank=True, max_length=150, null=True, verbose_name='码值')),
                ('activity_time', models.DateTimeField(verbose_name='激活时间')),
                ('delivery_time', models.DateTimeField(blank=True, null=True, verbose_name='出库时间')),
                ('purchase_time', models.DateTimeField(verbose_name='购买日期')),
                ('grade', models.CharField(max_length=10, verbose_name='评价星级（1-5）')),
                ('comment', models.TextField(blank=True, null=True, verbose_name='评论内容')),
                ('register_time', models.DateTimeField(verbose_name='产品注册时间')),
                ('cs_id', models.CharField(max_length=60, verbose_name='用户id')),
                ('nick_name', models.CharField(blank=True, max_length=230, null=True, verbose_name='昵称')),
                ('area', models.CharField(blank=True, max_length=150, null=True, verbose_name='所在地区')),
                ('gender', models.CharField(max_length=10, verbose_name='性别')),
                ('check_status', models.CharField(max_length=60, verbose_name='审核状态')),
                ('name', models.CharField(blank=True, max_length=150, null=True, verbose_name='真实姓名')),
                ('birthday', models.DateTimeField(blank=True, null=True, verbose_name='真实生日')),
                ('cs_gender', models.CharField(blank=True, max_length=10, null=True, verbose_name='真实性别')),
                ('cs_mobile', models.CharField(blank=True, max_length=60, null=True, verbose_name='真实手机号')),
                ('cs_area', models.CharField(blank=True, max_length=150, null=True, verbose_name='真实区域')),
                ('cs_address', models.CharField(blank=True, max_length=230, null=True, verbose_name='真实地址')),
                ('living_area', models.CharField(blank=True, max_length=60, null=True, verbose_name='家庭面积')),
                ('family', models.CharField(blank=True, max_length=150, null=True, verbose_name='家庭成员')),
                ('habit', models.CharField(blank=True, max_length=150, null=True, verbose_name='兴趣爱好')),
                ('other_habit', models.CharField(blank=True, max_length=150, null=True, verbose_name='其他兴趣')),
                ('auth_time', models.DateTimeField(verbose_name='授权时间')),
                ('order_status', models.SmallIntegerField(choices=[(0, '已取消'), (1, '未处理'), (2, '已完成')], db_index=True, default=1, verbose_name='单据状态')),
                ('process_tag', models.SmallIntegerField(choices=[(0, '未处理'), (1, '待核实'), (2, '已确认'), (3, '待清理'), (4, '已处理'), (5, '驳回'), (6, '特殊订单')], default=0, verbose_name='处理标签')),
                ('mistake_tag', models.SmallIntegerField(choices=[(0, '正常'), (1, '已导入过的订单'), (2, '待确认重复订单')], default=0, verbose_name='错误列表')),
            ],
            options={
                'verbose_name': 'crm-微信公众号原始单据-查询',
                'verbose_name_plural': 'crm-微信公众号原始单据-查询',
                'db_table': 'crm_webchart_oriorderinfo',
            },
        ),
        migrations.CreateModel(
            name='WarrantyInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('creator', models.CharField(default='system', max_length=30, verbose_name='创建者')),
                ('warranty_sn', models.CharField(max_length=150, unique=True, verbose_name='延保码')),
                ('batch_name', models.CharField(max_length=150, verbose_name='所属批次')),
                ('duration', models.IntegerField(verbose_name='延保时长')),
                ('goods_name', models.CharField(max_length=150, verbose_name='商品型号')),
                ('produce_sn', models.CharField(max_length=150, verbose_name='序列号')),
                ('purchase_time', models.DateTimeField(verbose_name='购买时间')),
                ('register_time', models.DateTimeField(blank=True, null=True, verbose_name='产品注册时间')),
                ('webchat_name', models.CharField(blank=True, max_length=150, null=True, verbose_name='微信昵称')),
                ('name', models.CharField(blank=True, max_length=150, null=True, verbose_name='姓名')),
                ('birthday', models.DateTimeField(blank=True, null=True, verbose_name='生日')),
                ('gender', models.CharField(max_length=10, verbose_name='性别')),
                ('area', models.CharField(blank=True, max_length=150, null=True, verbose_name='真实区域')),
                ('living_area', models.CharField(blank=True, max_length=60, null=True, verbose_name='家庭面积')),
                ('family', models.CharField(blank=True, max_length=150, null=True, verbose_name='家庭成员')),
                ('habit', models.CharField(blank=True, max_length=150, null=True, verbose_name='兴趣爱好')),
                ('other_habit', models.CharField(blank=True, max_length=150, null=True, verbose_name='其他兴趣')),
                ('order_status', models.SmallIntegerField(choices=[(0, '已取消'), (1, '未处理'), (2, '已完成')], db_index=True, default=1, verbose_name='单据状态')),
                ('process_tag', models.SmallIntegerField(choices=[(0, '未处理'), (1, '待核实'), (2, '已确认'), (3, '待清理'), (4, '已处理'), (5, '驳回'), (6, '特殊订单')], default=0, verbose_name='处理标签')),
                ('mistake_tag', models.SmallIntegerField(choices=[(0, '正常'), (1, '已导入过的订单'), (2, '待确认重复订单')], default=0, verbose_name='错误列表')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customers.CustomerInfo', verbose_name='客户')),
            ],
            options={
                'verbose_name': 'crm-微信公众号延保码-查询',
                'verbose_name_plural': 'crm-微信公众号延保码-查询',
                'db_table': 'crm_webchart_warranty',
            },
        ),
        migrations.CreateModel(
            name='WebchatInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=False, verbose_name='删除标记')),
                ('creator', models.CharField(default='system', max_length=30, verbose_name='创建者')),
                ('type', models.CharField(max_length=60, verbose_name='机器类别')),
                ('goods_name', models.CharField(max_length=150, verbose_name='产品名称')),
                ('goods_series', models.CharField(max_length=60, verbose_name='货品序号')),
                ('goods_id', models.CharField(max_length=150, verbose_name='型号')),
                ('produce_sn', models.CharField(max_length=150, verbose_name='码值')),
                ('activity_time', models.DateTimeField(verbose_name='激活时间')),
                ('delivery_time', models.DateTimeField(blank=True, null=True, verbose_name='出库时间')),
                ('purchase_time', models.DateTimeField(verbose_name='购买日期')),
                ('comment', models.TextField(blank=True, null=True, verbose_name='评论内容')),
                ('register_time', models.DateTimeField(verbose_name='产品注册时间')),
                ('cs_id', models.CharField(max_length=60, verbose_name='用户id')),
                ('nick_name', models.CharField(blank=True, max_length=230, null=True, verbose_name='昵称')),
                ('area', models.CharField(blank=True, max_length=150, null=True, verbose_name='所在地区')),
                ('gender', models.CharField(max_length=10, verbose_name='性别')),
                ('name', models.CharField(blank=True, max_length=150, null=True, verbose_name='真实姓名')),
                ('birthday', models.DateTimeField(blank=True, null=True, verbose_name='真实生日')),
                ('cs_gender', models.CharField(blank=True, max_length=10, null=True, verbose_name='真实性别')),
                ('cs_area', models.CharField(blank=True, max_length=150, null=True, verbose_name='真实区域')),
                ('cs_address', models.CharField(blank=True, max_length=230, null=True, verbose_name='真实地址')),
                ('living_area', models.CharField(blank=True, max_length=60, null=True, verbose_name='家庭面积')),
                ('family', models.CharField(blank=True, max_length=150, null=True, verbose_name='家庭成员')),
                ('habit', models.CharField(blank=True, max_length=150, null=True, verbose_name='兴趣爱好')),
                ('other_habit', models.CharField(blank=True, max_length=150, null=True, verbose_name='其他兴趣')),
                ('order_status', models.SmallIntegerField(choices=[(0, '已取消'), (1, '未处理'), (2, '已完成')], db_index=True, default=1, verbose_name='单据状态')),
                ('process_tag', models.SmallIntegerField(choices=[(0, '未处理'), (1, '待核实'), (2, '已确认'), (3, '待清理'), (4, '已处理'), (5, '驳回'), (6, '特殊订单')], default=0, verbose_name='处理标签')),
                ('mistake_tag', models.SmallIntegerField(choices=[(0, '正常'), (1, '已导入过的订单'), (2, '待确认重复订单')], default=0, verbose_name='错误列表')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customers.CustomerInfo', verbose_name='客户')),
            ],
            options={
                'verbose_name': 'CRM-微信公众号单据-查询',
                'verbose_name_plural': 'CRM-微信公众号单据-查询',
                'db_table': 'crm_webchart_orderinfo',
            },
        ),
        migrations.CreateModel(
            name='OWNumber',
            fields=[
            ],
            options={
                'verbose_name': 'crm-微信公众号原始延保码-未递交',
                'verbose_name_plural': 'crm-微信公众号原始延保码-未递交',
                'proxy': True,
                'indexes': [],
            },
            bases=('webchatcus.oriwarrantyinfo',),
        ),
        migrations.CreateModel(
            name='OWOrder',
            fields=[
            ],
            options={
                'verbose_name': 'crm-微信公众号原始单据-未递交',
                'verbose_name_plural': 'crm-微信公众号原始单据-未递交',
                'proxy': True,
                'indexes': [],
            },
            bases=('webchatcus.oriwebchatinfo',),
        ),
        migrations.CreateModel(
            name='WNumber',
            fields=[
            ],
            options={
                'verbose_name': 'crm-微信公众号延保码-未递交',
                'verbose_name_plural': 'crm-微信公众号延保码-未递交',
                'proxy': True,
                'indexes': [],
            },
            bases=('webchatcus.warrantyinfo',),
        ),
        migrations.CreateModel(
            name='WOrder',
            fields=[
            ],
            options={
                'verbose_name': 'crm-微信公众号单据-未递交',
                'verbose_name_plural': 'crm-微信公众号单据-未递交',
                'proxy': True,
                'indexes': [],
            },
            bases=('webchatcus.webchatinfo',),
        ),
    ]