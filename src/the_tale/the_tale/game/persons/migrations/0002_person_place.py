# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('places', '0001_initial'),
        ('persons', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='place',
            field=models.ForeignKey(related_name='persons', on_delete=django.db.models.deletion.PROTECT, to='places.Place'),
            preserve_default=True,
        ),
    ]
