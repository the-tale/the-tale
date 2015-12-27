# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import rels.django
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bills', '0001_initial'),
        ('persons', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Building',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_at_turn', models.BigIntegerField(default=0)),
                ('x', models.BigIntegerField()),
                ('y', models.BigIntegerField()),
                ('state', rels.django.RelationIntegerField(db_index=True)),
                ('type', rels.django.RelationIntegerField()),
                ('integrity', models.FloatField(default=1.0)),
                ('data', models.TextField(default='{}')),
                ('person', models.ForeignKey(to='persons.Person', unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('x', models.BigIntegerField()),
                ('y', models.BigIntegerField()),
                ('created_at', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0), auto_now_add=True)),
                ('created_at_turn', models.BigIntegerField(default=0)),
                ('updated_at_turn', models.BigIntegerField(default=0)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_frontier', models.BooleanField(default=False)),
                ('name', models.CharField(max_length=150, db_index=True)),
                ('description', models.TextField(default='', blank=True)),
                ('size', models.IntegerField()),
                ('expected_size', models.IntegerField(default=0)),
                ('goods', models.IntegerField(default=0)),
                ('keepers_goods', models.IntegerField(default=0)),
                ('production', models.IntegerField(default=100)),
                ('safety', models.FloatField(default=0.75)),
                ('freedom', models.FloatField(default=1.0)),
                ('transport', models.FloatField(default=1.0)),
                ('tax', models.FloatField(default=0.0)),
                ('stability', models.FloatField(default=1.0)),
                ('data', models.TextField(default='{}')),
                ('heroes_number', models.IntegerField(default=0)),
                ('habit_honor_positive', models.FloatField(default=0)),
                ('habit_honor_negative', models.FloatField(default=0)),
                ('habit_peacefulness_positive', models.FloatField(default=0)),
                ('habit_peacefulness_negative', models.FloatField(default=0)),
                ('habit_honor', models.FloatField(default=0)),
                ('habit_peacefulness', models.FloatField(default=0)),
                ('modifier', rels.django.RelationIntegerField(default=None, null=True, blank=True)),
                ('race', rels.django.RelationIntegerField()),
                ('persons_changed_at_turn', models.BigIntegerField(default=0)),
            ],
            options={
                'ordering': ('name',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ResourceExchange',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('resource_1', rels.django.RelationIntegerField()),
                ('resource_2', rels.django.RelationIntegerField()),
                ('bill', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='bills.Bill', null=True)),
                ('place_1', models.ForeignKey(related_name='+', to='places.Place', null=True)),
                ('place_2', models.ForeignKey(related_name='+', to='places.Place', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='building',
            name='place',
            field=models.ForeignKey(to='places.Place'),
            preserve_default=True,
        ),
    ]
