# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MapInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=datetime.datetime(2000, 1, 1, 0, 0), auto_now_add=True)),
                ('turn_number', models.BigIntegerField(db_index=True)),
                ('width', models.IntegerField()),
                ('height', models.IntegerField()),
                ('terrain', models.TextField(default=b'[]')),
                ('cells', models.TextField(default=b'')),
                ('statistics', models.TextField(default=b'{}')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='WorldInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('data', models.TextField(default=b'', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='mapinfo',
            name='world',
            field=models.ForeignKey(related_name='+', to='map.WorldInfo'),
            preserve_default=True,
        ),
    ]
