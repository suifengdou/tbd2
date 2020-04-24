# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2020-04-20 17:51
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('workorderinvoice', '0025_auto_20200415_1331'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoiceorder',
            name='sign_company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='inv_sign_company', to='company.CompanyInfo', verbose_name='创建公司'),
        ),
    ]
