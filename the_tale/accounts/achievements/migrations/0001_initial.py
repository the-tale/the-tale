# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import rels.django
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('collections', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountAchievements',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('achievements', models.TextField(default=b'{}')),
                ('points', models.IntegerField(default=0)),
                ('account', models.ForeignKey(to=settings.AUTH_USER_MODEL, unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Achievement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('group', rels.django.RelationIntegerField(db_index=True)),
                ('type', rels.django.RelationIntegerField(db_index=True)),
                ('caption', models.CharField(max_length=128)),
                ('description', models.CharField(max_length=1024)),
                ('order', models.IntegerField()),
                ('approved', models.BooleanField(default=False)),
                ('barrier', models.IntegerField()),
                ('points', models.IntegerField()),
                ('item_1', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, default=None, to='collections.Item', null=True)),
                ('item_2', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, default=None, to='collections.Item', null=True)),
                ('item_3', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, default=None, to='collections.Item', null=True)),
            ],
            options={
                'permissions': (('edit_achievement', '\u041c\u043e\u0436\u0435\u0442 \u0441\u043e\u0437\u0434\u0430\u0432\u0430\u0442\u044c \u0438 \u0440\u0435\u0434\u0430\u043a\u0442\u0438\u0440\u043e\u0432\u0430\u0442\u044c \u0434\u043e\u0441\u0442\u0438\u0436\u0435\u043d\u0438\u044f'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GiveAchievementTask',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('account', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
                ('achievement', models.ForeignKey(to='achievements.Achievement')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
