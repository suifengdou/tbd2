# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-04-20 13:14
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_auto_20190408_2119'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='emailverifyrecord',
            table='usr_emailverifyrecord',
        ),
        migrations.AlterModelTable(
            name='userprofile',
            table='usr_userprofile',
        ),
    ]
