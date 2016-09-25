# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ratings', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ratingplaces',
            name='politics_power_place',
            field=models.IntegerField(default=0, db_index=True),
        ),
        migrations.AddField(
            model_name='ratingvalues',
            name='politics_power',
            field=models.FloatField(default=0, db_index=True),
        ),
    ]
