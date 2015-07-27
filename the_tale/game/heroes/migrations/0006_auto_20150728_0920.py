# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import rels.django


class Migration(migrations.Migration):

    dependencies = [
        ('heroes', '0005_hero_stat_politics_multiplier'),
    ]

    operations = [
        migrations.AlterField(
            model_name='heropreferences',
            name='energy_regeneration_type',
            field=rels.django.RelationIntegerField(),
        ),
    ]
