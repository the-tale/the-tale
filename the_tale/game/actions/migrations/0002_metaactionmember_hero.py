# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('heroes', '0001_initial'),
        ('actions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='metaactionmember',
            name='hero',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.PROTECT, to='heroes.Hero'),
            preserve_default=True,
        ),
    ]
