# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('heroes', '0004_hero_actual_bills'),
    ]

    operations = [
        migrations.AddField(
            model_name='hero',
            name='stat_politics_multiplier',
            field=models.FloatField(default=0),
        ),
    ]
