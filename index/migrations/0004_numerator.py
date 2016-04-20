# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-04-16 17:44
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0003_auto_20160312_2236'),
    ]

    operations = [
        migrations.CreateModel(
            name='Numerator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_number', models.IntegerField(db_index=True, default=1)),
                ('departament', models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='index.OrganizationUnits')),
            ],
        ),
    ]