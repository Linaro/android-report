# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2021-02-17 05:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lkft', '0017_auto_20210216_1313'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testcase',
            name='suite',
            field=models.CharField(max_length=256),
        ),
        migrations.AlterField(
            model_name='testsuite',
            name='name',
            field=models.CharField(max_length=256),
        ),
    ]