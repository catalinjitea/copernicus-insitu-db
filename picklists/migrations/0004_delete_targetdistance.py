# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-07-17 14:31
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('picklists', '0003_essentialclimatevariable'),
    ]

    operations = [
        migrations.DeleteModel(
            name='TargetDistance',
        ),
    ]