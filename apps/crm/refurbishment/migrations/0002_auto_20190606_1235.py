# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-06-06 12:35
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('refurbishment', '0001_initial'),
        ('machine', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='orirefurbishinfo',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='orirefurbishinfo_createdby', to=settings.AUTH_USER_MODEL, verbose_name='翻新人'),
        ),
        migrations.AddField(
            model_name='orirefurbishinfo',
            name='goods_name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='machine.MachineInfo', verbose_name='机器名称'),
        ),
        migrations.AlterIndexTogether(
            name='apprasialinfo',
            index_together=set([('appraisal',)]),
        ),
        migrations.CreateModel(
            name='PrivateOriRefurbishInfo',
            fields=[
            ],
            options={
                'verbose_name': '私有翻新列表',
                'verbose_name_plural': '私有翻新列表',
                'proxy': True,
                'indexes': [],
            },
            bases=('refurbishment.orirefurbishinfo',),
        ),
        migrations.CreateModel(
            name='PrivateRefurbishTechSummary',
            fields=[
            ],
            options={
                'verbose_name': '私有技术员翻新统计列表',
                'verbose_name_plural': '私有技术员翻新统计列表',
                'proxy': True,
                'indexes': [],
            },
            bases=('refurbishment.refurbishtechsummary',),
        ),
    ]
