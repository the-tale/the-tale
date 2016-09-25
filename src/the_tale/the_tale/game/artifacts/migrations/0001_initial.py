# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings
import rels.django


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mobs', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArtifactRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('type', rels.django.RelationIntegerField()),
                ('power_type', rels.django.RelationIntegerField()),
                ('state', rels.django.RelationIntegerField()),
                ('rare_effect', rels.django.RelationIntegerField()),
                ('epic_effect', rels.django.RelationIntegerField()),
                ('special_effect', rels.django.RelationIntegerField(default=666)),
                ('level', models.IntegerField(default=0)),
                ('uuid', models.CharField(unique=True, max_length=32)),
                ('name', models.CharField(unique=True, max_length=32, db_index=True)),
                ('description', models.TextField(default='', blank=True)),
                ('data', models.TextField(default=b'{}')),
                ('editor', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('mob', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='mobs.MobRecord', null=True)),
            ],
            options={
                'permissions': (('create_artifactrecord', '\u041c\u043e\u0436\u0435\u0442 \u043f\u0440\u0435\u0434\u043b\u0430\u0433\u0430\u0442\u044c \u0430\u0440\u0442\u0435\u0444\u0430\u043a\u0442\u044b'), ('moderate_artifactrecord', '\u041c\u043e\u0436\u0435\u0442 \u0443\u0442\u0432\u0435\u0440\u0436\u0434\u0430\u0442\u044c \u0430\u0440\u0442\u0435\u0444\u0430\u043a\u0442\u044b')),
            },
            bases=(models.Model,),
        ),
    ]
