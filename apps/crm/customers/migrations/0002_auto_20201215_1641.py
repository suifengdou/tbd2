# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-12-15 16:41
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customerinfo',
            old_name='wechat',
            new_name='webchat',
        ),
    ]