# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2021-04-08 09:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lkft', '0018_auto_20210407_0804'),
    ]

    operations = [
        migrations.AddField(
            model_name='reportbuild',
            name='metadata_url',
            field=models.URLField(null=True),
        ),
    ]