# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import rels.django


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CompanionRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('state', rels.django.RelationIntegerField(db_index=True)),
                ('type', rels.django.RelationIntegerField(db_index=True)),
                ('dedication', rels.django.RelationIntegerField(db_index=True)),
                ('archetype', rels.django.RelationIntegerField(blank=True)),
                ('mode', rels.django.RelationIntegerField(blank=True)),
                ('max_health', models.IntegerField(default=1)),
                ('data', models.TextField(default=b'{}')),
            ],
            options={
                'permissions': (('create_companionrecord', '\u041c\u043e\u0436\u0435\u0442 \u0441\u043e\u0437\u0434\u0430\u0432\u0430\u0442\u044c \u0441\u043f\u0443\u0442\u043d\u0438\u043a\u043e\u0432'), ('moderate_companionrecord', '\u041c\u043e\u0436\u0435\u0442 \u0443\u0442\u0432\u0435\u0440\u0436\u0434\u0430\u0442\u044c \u0441\u043f\u0443\u0442\u043d\u0438\u043a\u043e\u0432')),
            },
            bases=(models.Model,),
        ),
    ]
