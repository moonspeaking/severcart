# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-08-30 11:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='settings',
            name='print_bar_code',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='settings',
            name='print_name_obj',
            field=models.BooleanField(default=False),
        ),
    ]
