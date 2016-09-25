# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountItems',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('items', models.TextField(default=b'{}')),
                ('account', models.ForeignKey(to=settings.AUTH_USER_MODEL, unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('approved', models.BooleanField(default=False)),
                ('caption', models.CharField(max_length=100)),
                ('description', models.TextField(max_length=1000)),
            ],
            options={
                'permissions': (('edit_collection', '\u041c\u043e\u0436\u0435\u0442 \u0441\u043e\u0437\u0434\u0430\u0432\u0430\u0442\u044c \u0438 \u0440\u0435\u0434\u0430\u043a\u0442\u0438\u0440\u043e\u0432\u0430\u0442\u044c \u043a\u043e\u043b\u043b\u0435\u043a\u0446\u0438\u0438'), ('moderate_collection', '\u041c\u043e\u0436\u0435\u0442 \u0443\u0442\u0432\u0435\u0440\u0436\u0434\u0430\u0442\u044c \u043a\u043e\u043b\u043b\u0435\u043a\u0446\u0438\u0438')),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GiveItemTask',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('account', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('approved', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('caption', models.CharField(max_length=100)),
                ('text', models.TextField()),
            ],
            options={
                'permissions': (('edit_item', '\u041c\u043e\u0436\u0435\u0442 \u0441\u043e\u0437\u0434\u0430\u0432\u0430\u0442\u044c \u0438 \u0440\u0435\u0434\u0430\u043a\u0442\u0438\u0440\u043e\u0432\u0430\u0442\u044c \u043f\u0440\u0435\u0434\u043c\u0435\u0442\u044b'), ('moderate_item', '\u041c\u043e\u0436\u0435\u0442 \u0443\u0442\u0432\u0435\u0440\u0436\u0434\u0430\u0442\u044c \u043f\u0440\u0435\u0434\u043c\u0435\u0442\u044b')),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Kit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('approved', models.BooleanField(default=False)),
                ('caption', models.CharField(max_length=100)),
                ('description', models.TextField(max_length=1000)),
                ('collection', models.ForeignKey(to='collections.Collection', on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'permissions': (('edit_kit', '\u041c\u043e\u0436\u0435\u0442 \u0441\u043e\u0437\u0434\u0430\u0432\u0430\u0442\u044c \u0438 \u0440\u0435\u0434\u0430\u043a\u0442\u0438\u0440\u043e\u0432\u0430\u0442\u044c \u043d\u0430\u0431\u043e\u0440\u044b'), ('moderate_kit', '\u041c\u043e\u0436\u0435\u0442 \u0443\u0442\u0432\u0435\u0440\u0436\u0434\u0430\u0442\u044c \u043d\u0430\u0431\u043e\u0440\u044b')),
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='item',
            name='kit',
            field=models.ForeignKey(to='collections.Kit', on_delete=django.db.models.deletion.PROTECT),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='giveitemtask',
            name='item',
            field=models.ForeignKey(to='collections.Item'),
            preserve_default=True,
        ),
    ]
