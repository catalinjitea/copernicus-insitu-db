# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-07-17 14:31
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('insitu', '0007_auto_20170712_1626'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productrequirement',
            name='distance_to_target',
        ),
    ]
