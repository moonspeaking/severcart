# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-07-16 23:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('smtp_server', models.CharField(max_length=256, null=True)),
                ('smtp_port', models.IntegerField(db_index=True, null=True)),
                ('email_sender', models.EmailField(blank=True, max_length=254, null=True)),
                ('smtp_login', models.CharField(max_length=256, null=True)),
                ('smtp_password', models.CharField(max_length=256, null=True)),
                ('use_ssl', models.BooleanField(default=False)),
                ('use_tls', models.BooleanField(default=False)),
                ('page_format', models.CharField(default='A4', max_length=2, null=True)),
            ],
        ),
    ]
