# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2022-11-02 13:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lkft', '0030_auto_20221018_0809'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reportjob',
            name='job_name',
            field=models.CharField(max_length=256),
        ),
    ]
