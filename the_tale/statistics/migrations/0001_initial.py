# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import rels.django


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Record',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField()),
                ('type', rels.django.RelationIntegerField(db_index=True)),
                ('value_int', models.BigIntegerField()),
                ('value_float', models.FloatField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
