# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import rels.django


class Migration(migrations.Migration):

    dependencies = [
        ('mobs', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='mobrecord',
            name='communication_gestures',
            field=rels.django.RelationIntegerField(default=0, db_index=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='mobrecord',
            name='communication_telepathic',
            field=rels.django.RelationIntegerField(default=0, db_index=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='mobrecord',
            name='communication_verbal',
            field=rels.django.RelationIntegerField(default=0, db_index=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='mobrecord',
            name='intellect_level',
            field=rels.django.RelationIntegerField(default=0, db_index=True),
            preserve_default=False,
        ),
    ]
