# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import rels.django
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bills', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Actor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uid', models.CharField(unique=True, max_length=16)),
                ('bill', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to='bills.Bill', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Record',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', rels.django.RelationIntegerField(db_index=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_at_turn', models.IntegerField()),
                ('text', models.TextField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RecordToActor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('role', rels.django.RelationIntegerField()),
                ('actor', models.ForeignKey(to='chronicle.Actor', on_delete=django.db.models.deletion.PROTECT)),
                ('record', models.ForeignKey(to='chronicle.Record')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='record',
            name='actors',
            field=models.ManyToManyField(to='chronicle.Actor', through='chronicle.RecordToActor'),
            preserve_default=True,
        ),
    ]
