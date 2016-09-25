# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bills', '0002_actor_place'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bill',
            name='chronicle_on_ended',
        ),
        migrations.RemoveField(
            model_name='bill',
            name='duration',
        ),
        migrations.RemoveField(
            model_name='bill',
            name='ends_at_turn',
        ),
    ]
