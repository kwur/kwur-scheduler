# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-12 17:34
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0010_auto_20160905_2159'),
    ]

    operations = [
        migrations.AlterField(
            model_name='show',
            name='dj',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='show', to='scheduler.BaseUser'),
        ),
    ]
