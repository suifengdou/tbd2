# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-11-27 10:04
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('dialog', '0001_initial'),
        ('compensation', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='diatooriist',
            name='dialog_order',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='com_dialog_tb', to='dialog.OriDetailTB', verbose_name='对话明细'),
        ),
        migrations.AddField(
            model_name='diatooriist',
            name='ori_order',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='com_create', to='compensation.OriCompensation', verbose_name='原始补偿单'),
        ),
        migrations.AddField(
            model_name='batchinfo',
            name='batch_order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='compensation.BatchCompensation', verbose_name='批次单'),
        ),
        migrations.AddField(
            model_name='batchinfo',
            name='compensation_order',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='compensation.Compensation', verbose_name='补偿单'),
        ),
        migrations.CreateModel(
            name='BCheck',
            fields=[
            ],
            options={
                'verbose_name': 'CRM-补偿汇总单-未结算',
                'verbose_name_plural': 'CRM-补偿汇总单-未结算',
                'proxy': True,
                'indexes': [],
            },
            bases=('compensation.batchcompensation',),
        ),
        migrations.CreateModel(
            name='BICheck',
            fields=[
            ],
            options={
                'verbose_name': 'CRM-补偿汇总明细单-未结算',
                'verbose_name_plural': 'CRM-补偿汇总明细单-未结算',
                'proxy': True,
                'indexes': [],
            },
            bases=('compensation.batchinfo',),
        ),
        migrations.CreateModel(
            name='BSubmit',
            fields=[
            ],
            options={
                'verbose_name': 'CRM-补偿汇总单-未审核',
                'verbose_name_plural': 'CRM-补偿汇总单-未审核',
                'proxy': True,
                'indexes': [],
            },
            bases=('compensation.batchcompensation',),
        ),
        migrations.CreateModel(
            name='CCheck',
            fields=[
            ],
            options={
                'verbose_name': 'CRM-补偿单-未审核',
                'verbose_name_plural': 'CRM-补偿单-未审核',
                'proxy': True,
                'indexes': [],
            },
            bases=('compensation.compensation',),
        ),
        migrations.CreateModel(
            name='OCCheck',
            fields=[
            ],
            options={
                'verbose_name': 'CRM-原始补偿单-未审核',
                'verbose_name_plural': 'CRM-原始补偿单-未审核',
                'proxy': True,
                'indexes': [],
            },
            bases=('compensation.oricompensation',),
        ),
    ]
