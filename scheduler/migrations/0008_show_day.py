# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-31 17:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0007_auto_20160830_2021'),
    ]

    operations = [
        migrations.AddField(
            model_name='show',
            name='day',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
