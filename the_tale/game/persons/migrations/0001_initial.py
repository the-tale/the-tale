# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import rels.django


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=datetime.datetime(2000, 1, 1, 0, 0), auto_now_add=True)),
                ('created_at_turn', models.IntegerField(default=0)),
                ('out_game_at', models.DateTimeField(default=datetime.datetime(2000, 1, 1, 0, 0))),
                ('state', rels.django.RelationIntegerField()),
                ('gender', rels.django.RelationIntegerField()),
                ('race', rels.django.RelationIntegerField()),
                ('type', rels.django.RelationIntegerField()),
                ('friends_number', models.IntegerField(default=0)),
                ('enemies_number', models.IntegerField(default=0)),
                ('name', models.CharField(max_length=100, db_index=True)),
                ('data', models.TextField(default='{}')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SocialConnection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_at_turn', models.BigIntegerField()),
                ('out_game_at', models.DateTimeField(default=None, null=True)),
                ('out_game_at_turn', models.BigIntegerField(default=None, null=True)),
                ('connection', rels.django.RelationIntegerField()),
                ('state', rels.django.RelationIntegerField()),
                ('person_1', models.ForeignKey(related_name='+', to='persons.Person')),
                ('person_2', models.ForeignKey(related_name='+', to='persons.Person')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
