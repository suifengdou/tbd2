# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-04-08 21:19
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20190329_0914'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='emailverifyrecord',
            table='emailverifyrecord',
        ),
        migrations.AlterModelTable(
            name='userprofile',
            table='userprofile',
        ),
    ]