# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import rels.django


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MetaAction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('type', rels.django.RelationIntegerField(default=None)),
                ('percents', models.FloatField(default=0.0)),
                ('state', models.CharField(default=b'uninitialized', max_length=50)),
                ('data', models.TextField(default=b'{}')),
                ('bundle_id', models.BigIntegerField(null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MetaActionMember',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('context', models.TextField(default=b'{}')),
                ('role', models.CharField(max_length=32)),
                ('action', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.PROTECT, to='actions.MetaAction')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
