# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-06-25 15:55
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('qcorder', '0002_qcoriinfo_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='QCSubmitOriInfo',
            fields=[
            ],
            options={
                'verbose_name': '未递交原始质检单',
                'verbose_name_plural': '未递交原始质检单',
                'proxy': True,
                'indexes': [],
            },
            bases=('qcorder.qcoriinfo',),
        ),
        migrations.AlterModelOptions(
            name='qcoriinfo',
            options={'verbose_name': '原始质检单明细表', 'verbose_name_plural': '原始质检单明细表'},
        ),
    ]