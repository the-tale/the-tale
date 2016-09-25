# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bills', '0001_initial'),
        ('places', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='actor',
            name='place',
            field=models.ForeignKey(related_name='+', to='places.Place', null=True),
            preserve_default=True,
        ),
    ]
