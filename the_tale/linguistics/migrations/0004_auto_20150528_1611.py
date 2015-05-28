# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import rels.django


class Migration(migrations.Migration):

    dependencies = [
        ('linguistics', '0003_auto_20150513_0645'),
    ]

    operations = [
        migrations.AddField(
            model_name='contribution',
            name='state',
            field=rels.django.RelationIntegerField(default=1, db_index=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='contribution',
            name='type',
            field=rels.django.RelationIntegerField(db_index=True),
        ),
    ]
