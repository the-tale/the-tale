# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chronicle', '0001_initial'),
        ('places', '0001_initial'),
        ('persons', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='actor',
            name='person',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to='persons.Person', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='actor',
            name='place',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to='places.Place', null=True),
            preserve_default=True,
        ),
    ]
