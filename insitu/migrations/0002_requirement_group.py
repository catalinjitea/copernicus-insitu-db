# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-07-19 09:01
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('picklists', '0002_requirementgroup'),
        ('insitu', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='requirement',
            name='group',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='picklists.RequirementGroup'),
            preserve_default=False,
        ),
    ]
