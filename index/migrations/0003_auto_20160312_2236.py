# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-12 22:36
from __future__ import unicode_literals

from django.db import migrations


def load_stores_from_fixture(apps, schema_editor):
    from django.core.management import call_command
    call_command("loaddata", "stores")

class Migration(migrations.Migration):

    dependencies = [
        ('index', '0002_auto_20160312_2210'),
    ]

    operations = [
        migrations.RunPython(load_stores_from_fixture),
    ]
