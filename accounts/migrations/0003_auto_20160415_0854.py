# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-15 08:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_anconuser_secret_key'),
    ]

    operations = [
        migrations.AlterField(
            model_name='anconuser',
            name='secret_key',
            field=models.CharField(db_index=True, max_length=64, null=True, unique=True, verbose_name='Secret key'),
        ),
    ]