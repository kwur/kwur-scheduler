# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-14 04:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0012_auto_20160912_1236'),
    ]

    operations = [
        migrations.AlterField(
            model_name='baseuser',
            name='credits',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
    ]
